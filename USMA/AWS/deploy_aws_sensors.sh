#!/bin/bash
# Still very rough. Should find a way to ensure sensor is up before trying to connect 
# Should move to Python

if [ -z "$1" ] || [ -z "$2" ]; then
   echo "USAGE:  ./deploy_aws_sensors.sh [num_of_sensors] [sensor_name]"
exit
fi

wget -q https://s3.amazonaws.com/downloads.alienvault.cloud/usm-anywhere/sensor-images/usm-anywhere-sensor-aws-vpc.template -O ./usm-anywhere-sensor-aws-vpc.template
x=1
while [ $x -le $1 ]
do
  aws cloudformation deploy --template-file usm-anywhere-sensor-aws-vpc.template --stack-name "${2}-${x}" --parameter-overrides KeyName=JohnO VpcId=vpc-198db97d NodeName="${2}-${x}" SubnetId=subnet-426c2a1a --capabilities CAPABILITY_IAM
  sleep 5
  echo "The instance has been deployed and it's IP address is"
  ip=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=${2}-${x}" --query "Reservations[*].Instances[*].NetworkInterfaces[*].Association.PublicIp" --output text)
  echo $ip
  echo "Giving the sensor a minute to fully boot"
  sleep 60
  ./add_sensor.py -u USM-Anywhere-Training@alienvault.com -p Password1! -d training-team-longterm-1-20171003.alienvault.cloud -s $ip
  x=$(( $x + 1 ))
done
