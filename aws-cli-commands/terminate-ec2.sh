#!/bin/bash

instance_id=$(aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=test" "Name=instance-state-name,Values=running" \
  --query "Reservations[0].Instances[0].InstanceId" \
  --output text)

if [ -n "$instance_id" ] && [ "$instance_id" != "None" ]; then
    aws ec2 terminate-instances --instance-ids $instance_id
    echo "Instance with ID $instance_id terminated."
else
    echo "No instance found with the specified tag."
fi