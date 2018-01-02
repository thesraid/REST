#!/bin/bash
wget -q https://s3.amazonaws.com/downloads.alienvault.cloud/usm-anywhere/sensor-images/usm-anywhere-sensor-aws-vpc.template -O ./usm-anywhere-sensor-aws-vpc.template
x=1
while [ $x -le $1 ]
do
  #touch "${x}_file"
  aws cloudformation deploy --template-file usm-anywhere-sensor-aws-vpc.template --stack-name "autodeploy${x}" --parameter-overrides KeyName=SKO2018 VpcId=vpc-a07eaec7 NodeName="autodeploy${x}" SubnetId=subnet-974bb8f0 --capabilities CAPABILITY_IAM
  x=$(( $x + 1 ))
done
