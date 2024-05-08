import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, EndpointConnectionError
from concurrent.futures import ThreadPoolExecutor
import time
from datetime import datetime , timezone
import logging

req_queue_url='https://sqs.us-east-1.amazonaws.com/905418031675/1228052438-req-queue'

sqs=boto3.client('sqs', region_name='us-east-1')

ec2=boto3.client('ec2', region_name='us-east-1')

group_name='app-tier'
max_instances_allowed = 19

logging.basicConfig(
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S') 

def launch_multiple_instances(count,name_prefix):
    try:
        resp=ec2.run_instances(
            ImageId='ami-0c9866a4bf8a73a59',
            InstanceType='t2.micro',
            KeyName='naveena_key_pair',
            SecurityGroupIds=['sg-088829a8df1318a1d'],
            MinCount=count,
            MaxCount=count,
            UserData="#!/bin/bash\nsu ec2-user -c 'cd /home/ec2-user/app/face_recognition_part2/model/ && echo \"[$(date)] Start running app...\" && MAX_MESSAGES=1 WAIT_TIME_SEC=3 VISIBILITY_TIMEOUT=10 python3 face_recognition.py'", 
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            "Key": "Group",
                            "Value": group_name
                        }
                    ]
                }
            ]
        )
        logging.info(f"[launcing_ec2_instance] succesfully launched instances count = {len(resp['Instances'])}")

        for i in range(len(resp['Instances'])):
            ec2.create_tags(
                Resources=[resp['Instances'][i]['InstanceId']], 
                Tags=[{'Key': 'Name', 'Value': f'{name_prefix}-{i}'}]
            )
            logging.info(f"added tags for instance {resp['Instances'][i]['InstanceId']}")

    except NoCredentialsError:
        logging.error("[launcing_ec2_instance] Credentials not available. Please provide valid AWS credentials.")
    except PartialCredentialsError:
        logging.error("[launcing_ec2_instance] Partial credentials provided. Please provide valid AWS credentials.")
    except Exception as e:
        logging.error(f"[launcing_ec2_instance] An error occurred: {str(e)}")  

def check_and_terminate_instance(count):
    response=ec2.describe_instances(
        Filters=[{
           'Name': 'tag:Group',
           'Values': [group_name]
        },{
            'Name': 'instance-state-name',
            'Values': ['running']
        }
       ]
    ) 
    terminate_instance_ids=[]
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            if len(terminate_instance_ids)>=count:
                break
            terminate_instance_ids.append(instance['InstanceId'])
        if len(terminate_instance_ids)>=count:
                break
    terminate_instance(terminate_instance_ids)
    return None

def terminate_instance(instance_ids):  
    if len(instance_ids)>0:
        ec2.terminate_instances(InstanceIds=instance_ids)
        logging.info(f"Instance {instance_ids} terminated")
    else:
        logging.info(f"Instance IDs is empty")

def get_number_of_instances(states):
    response=ec2.describe_instances(
        Filters=[{
           'Name': 'tag:Group',
           'Values': [group_name]
        },{
            'Name': 'instance-state-name',
            'Values': states
        }
       ]
    )

    number_of_instances=0
    for reservation in response['Reservations']:
        number_of_instances+=len(reservation["Instances"])

    return number_of_instances

def check_req_queue_length():
    logging.info("Started Autoscaling app...")
    name_prefix="app-tier-instance"
    empty_checks=0
    while True:
        try:
            response = sqs.get_queue_attributes(
                    QueueUrl=req_queue_url,
                    AttributeNames=['ApproximateNumberOfMessages']
                )
            number_of_messages = int(response['Attributes']['ApproximateNumberOfMessages'])
        
            number_of_app_tier_instances = get_number_of_instances(['running','pending'])

            number_of_running_instances = get_number_of_instances(['running'])

            if number_of_app_tier_instances<max_instances_allowed and number_of_messages > number_of_app_tier_instances:
                num_instances_needed=number_of_messages-number_of_app_tier_instances
                num_instances_create=min(max_instances_allowed-number_of_app_tier_instances,num_instances_needed)
                launch_multiple_instances(num_instances_create,name_prefix)
                time.sleep(30)

            elif number_of_running_instances>0 and number_of_messages < number_of_running_instances:
                if number_of_messages == 0:
                    empty_checks+=1
                else:
                    empty_checks = 0
                if empty_checks > 20:
                    check_and_terminate_instance(number_of_running_instances)
                    empty_checks = 0


        except NoCredentialsError:
            logging.error("Credentials not available. Please provide valid AWS credentials.")
        except PartialCredentialsError:
            logging.error("Partial credentials provided. Please provide valid AWS credentials.")
        except EndpointConnectionError:
            logging.error("Error connecting to the SQS endpoint. Please check your network connectivity or endpoint configuration.")
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")  
        
        finally:
            time.sleep(1)

if __name__=="__main__":
        check_req_queue_length()

    