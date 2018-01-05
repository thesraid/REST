#!/bin/bash
aws ec2 describe-instances --output text --query 'Reservations[].Instances[].Tags[?Key==`Name`].Value'
