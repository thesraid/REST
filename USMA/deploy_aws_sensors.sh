#!/bin/bash
if [ -z "$1" ] || [ -z "$2" ]; then
   echo "USAGE:  ./deploy_aws_sensors.sh [num_of_sensors] [sensor_name]"
exit
fi

wget -q https://s3.amazonaws.com/downloads.alienvault.cloud/usm-anywhere/sensor-images/usm-anywhere-sensor-aws-vpc.template -O ./usm-anywhere-sensor-aws-vpc.template
x=1
while [ $x -le $1 ]
do
  #echo "${x}_${2}"
  aws cloudformation deploy --template-file usm-anywhere-sensor-aws-vpc.template --stack-name "${2}-${x}" --parameter-overrides KeyName=SKO2018 VpcId=vpc-a07eaec7 NodeName="${2}-${x}" SubnetId=subnet-974bb8f0 --capabilities CAPABILITY_IAM
  x=$(( $x + 1 ))
done
