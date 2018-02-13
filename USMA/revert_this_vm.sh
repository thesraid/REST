#!/bin/bash
# Check if a file exists. If it does not then create it
# If it does exist then reset this VM
#
# This will prevent the following
# Cronjob to revert to snapshot is set to run at 10:00
# At 10:00 VM is reverted to running snapshot
# It's still 10:00 and as we are running from a past snapshot the VM thinks cron did not run
# At 10:00 VM is reverted to running snapshot
# It's still 10:00 and as we are running from a past snapshot the VM thinks cron did not run
# ...Repeats...
# At 10:01 the VM thinks it missed the cronjob so still runs it
# ...Repeats...
#
# Solution:
# cron job - Is there a file? > YES > Revert
# VM reverted and cronjob runs again immediately.
# cron job - Is there a file? > NO > Create file
#
#
# Next week
# cron job - Is there a file? > YES > Revert
# VM reverted and cronjob runs again immediately.
# cron job - Is there a file? > NO > Create file

if [ ! -f  /opt/reset_scripts/revert_me ]; then
    echo "Creating file to revert this VM during next cron run"
    touch /opt/reset_scripts/revert_me
else
    echo "Reverting to snapshot"
    govc snapshot.revert -vm "/AV/vm/_Production_Labs (DO NOT TOUCH)/USM Anywhere DC Prep (WG12)/JEOS_Prod1"
fi
