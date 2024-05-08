__copyright__   = "Copyright 2024, VISA Lab"
__license__     = "MIT"

import logging
import os
# import csv
# import sys
import torch
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
# from torchvision import datasets
# from torch.utils.data import DataLoader
import boto3
import json
from io import BytesIO
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, EndpointConnectionError


req_queue_url='https://sqs.us-east-1.amazonaws.com/905418031675/1228052438-req-queue'
resp_queue_url='https://sqs.us-east-1.amazonaws.com/905418031675/1228052438-resp-queue'

in_bucket_name='1228052438-in-bucket'
out_bucket_name='1228052438-out-bucket'

sqs=boto3.client('sqs', region_name='us-east-1')
s3=boto3.client('s3')


logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S')

mtcnn = MTCNN(image_size=240, margin=0, min_face_size=20) # initializing mtcnn for face detection
resnet = InceptionResnetV1(pretrained='vggface2').eval() # initializing resnet for face img to embeding conversion
# test_image = sys.argv[1]

def sendMessageToRespQueue(s3_file_name,result):
    message_body=s3_file_name+':'+result
    response = sqs.send_message(
        QueueUrl=resp_queue_url,
        MessageBody=message_body
    )
    logging.info(message_body)
    logging.info(f"Message sent to response queue successfully. Message ID: {response['MessageId']}")


def uploadResultToS3(s3_file_name,result):
    try:
        s3.put_object(Bucket=out_bucket_name, Key=s3_file_name, Body=result)
        logging.info(f'response uploaded to S3 Successfully to {s3_file_name}')
        # sendMessageToRespQueue(s3_file_name,result)
    except NoCredentialsError:
        logging.info('Credentials Not Available')

def uploadImageToS3(file_name,byte_io):
    try:
       s3.put_object(Body=byte_io, Bucket=in_bucket_name, Key=file_name, ContentType='image/jpeg') 
       logging.info(f"Image uploaded to S3 successfully to {file_name}")
    except NoCredentialsError:
        logging.info('Credentials Not Available')

def face_match(image_byte_array, data_path): # img_path= location of photo, data_path= location of data.pt
    # getting embedding matrix of the given img
    img=Image.open(image_byte_array)
    # print("s3 image",image1)
    face, prob = mtcnn(img, return_prob=True) # returns cropped face and probability
    emb = resnet(face.unsqueeze(0)).detach() # detech is to make required gradient false

    saved_data = torch.load('data.pt') # loading data.pt file
    embedding_list = saved_data[0] # getting embedding data
    name_list = saved_data[1] # getting list of names
    dist_list = [] # list of matched distances, minimum distance is used to identify the person

    for idx, emb_db in enumerate(embedding_list):
        dist = torch.dist(emb, emb_db).item()
        dist_list.append(dist)

    idx_min = dist_list.index(min(dist_list))
    return (name_list[idx_min], min(dist_list))

# result = face_match(test_image, 'data.pt')
# logging.info(result[0])

def process_images():
    try:
        logging.info("Started polling worker...")
        maxMessages = int(os.environ.get('MAX_MESSAGES', 10))
        visibilityTimeout = int(os.environ.get('VISIBILITY_TIMEOUT', 20))
        waitTime = int(os.environ.get('WAIT_TIME_SEC', 3))
        logging.info({"maxMessages":maxMessages,"visibilityTimeout":visibilityTimeout,"waitTime":waitTime})
        while True:
            response = sqs.receive_message(
                QueueUrl=req_queue_url,
                MaxNumberOfMessages=maxMessages,
                VisibilityTimeout=visibilityTimeout,
                WaitTimeSeconds=waitTime
            )
    
            messages = response.get('Messages',[])
    
            if messages:
                logging.info(f"Recieved Messages={len(messages)}")
                for message in messages:
                    logging.info(f"Received message: Message body {message['MessageId']}")

                    req_message=message['Body']
                   
                    req_message=json.loads(req_message)
                    
                    #check if key is present
                    file_name=req_message["key"]
                    image_byte_array=req_message["value"]

                    result=face_match(BytesIO(image_byte_array.encode('latin-1')),'data.pt')
                    logging.info(result)

                    fileName, extension=os.path.splitext(file_name)
                    
                    sendMessageToRespQueue(fileName,result[0])

                    receipt_handle=message['ReceiptHandle']
                    sqs.delete_message(
                        QueueUrl=req_queue_url,
                        ReceiptHandle=receipt_handle
                    )

                    uploadResultToS3(fileName,result[0])

                    uploadImageToS3(file_name,image_byte_array)
                    
                    
            else:
                logging.info("No messages received. Waiting for messages...")
    
    except NoCredentialsError:
        logging.info("Credentials not available. Please provide valid AWS credentials.")
    except PartialCredentialsError:
        logging.info("Partial credentials provided. Please provide valid AWS credentials.")
    except EndpointConnectionError:
        logging.info("Error connecting to the SQS endpoint. Please check your network connectivity or endpoint configuration.")
    except Exception as e:
        logging.exception(f"An error occurred: {str(e)}")
        
    

if __name__ == "__main__":
    try:
        process_images()
    except KeyboardInterrupt:
        logging.info("Terminated by user")
