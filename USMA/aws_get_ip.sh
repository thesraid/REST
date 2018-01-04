#!/bin/bash
aws ec2 describe-instances --filters "Name=tag:Name,Values=$1" --query "Reservations[*].Instances[*].NetworkInterfaces[*].Association.PublicIp" --output text
