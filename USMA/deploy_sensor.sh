#!/bin/bash
govc vm.destroy "/AV/vm/_Production_Labs (DO NOT TOUCH)/USM Anywhere Analyst Prep (WG13)/Sensor-WG13"
template=$(govc ls "/AV/vm/_Templates_/USM Anywhere Templates/Production_Sensor_Image/" | sort -n | tail -1)
govc vm.clone -on=false -net=WG13-01 -ds=/AV/datastore/AWC-004 -folder="/AV/vm/_Production_Labs (DO NOT TOUCH)/USM Anywhere Analyst Prep (WG13)" -vm "$template" "Sensor-WG13"
govc vm.network.change -net.address=00:50:56:12:34:56 -vm "/AV/vm/_Production_Labs (DO NOT TOUCH)/USM Anywhere Analyst Prep (WG13)/Sensor-WG13" ethernet-0 WG13-01
govc vm.network.change -vm "/AV/vm/_Production_Labs (DO NOT TOUCH)/USM Anywhere Analyst Prep (WG13)/Sensor-WG13" ethernet-1 WG13-01
govc vm.network.change -vm "/AV/vm/_Production_Labs (DO NOT TOUCH)/USM Anywhere Analyst Prep (WG13)/Sensor-WG13" ethernet-2 WG13-01
govc vm.network.change -vm "/AV/vm/_Production_Labs (DO NOT TOUCH)/USM Anywhere Analyst Prep (WG13)/Sensor-WG13" ethernet-3 WG13-01
govc vm.network.change -vm "/AV/vm/_Production_Labs (DO NOT TOUCH)/USM Anywhere Analyst Prep (WG13)/Sensor-WG13" ethernet-4 WG13-01
govc vm.power -on Sensor-WG13
