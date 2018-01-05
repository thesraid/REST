#!/bin/bash
if [ -z "$1" ] ; then
   echo "USAGE:  ./aws_get_ip.sh [sensor_instance_name]"
   echo ""
   echo "EXAMPLE: ./aws_get_ip.sh sko2018-tech-1"
   echo ""
   echo "EXAMPLE: ./aws_get_ip.sh sko2018-sales-1"
   echo ""
exit
fi

aws ec2 describe-instances --filters "Name=tag:Name,Values=$1" --query "Reservations[*].Instances[*].NetworkInterfaces[*].Association.PublicIp" --output text
