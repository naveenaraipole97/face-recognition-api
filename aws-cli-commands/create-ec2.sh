#!/bin/bash
aws ec2 run-instances \
    --image-id ami-0c093bd423e37dc8e  \
    --key-name "naveena_key_pair"    \
    --instance-type "t2.micro"    \
    --security-group-ids "sg-088829a8df1318a1d"   \
    --iam-instance-profile Arn=arn:aws:iam::905418031675:instance-profile/s3_sqs_full_access    \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=app-tier-test-1}]'   \
    --user-data "file:///Users/naveenakappala/Desktop/cc_project_part2/aws-cli-commands/userdata.sh"