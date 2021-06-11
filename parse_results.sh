#!/usr/bin/bash

RESULTS_DIR=/tmp
cd $RESULTS_DIR

for brd in `ls -d ????-????-????`; do

  PROC=`cat $brd/gb5_report.json | jq .metrics[7].value`
  MEM_TTL=`cat $brd/gb5_report.json | jq .metrics[23].value`

  echo -e "######################################\n########## $brd ############\n######################################\n$PROC\n$MEM_TTL"

  # Show memory part numbers
  cat $brd/dmidecode.txt | egrep "Size|Part\ Number" | grep -v Not\ Specified 
  
  # get disk info
  echo "############# Disks ###################"
  cat $brd/lsblk.txt | grep -v MODEL=\"\"

  # geekbench results
  echo "################ Geekbench 5 ###########"
  cat $brd/gb5_report.json | jq ".score, .multicore_score"

  # FIO tests
  echo "################ FIO ###########"
  cat $brd/fio.json | jq '.jobs[].read.iops, .jobs[].read.lat_ns.mean, .jobs[].write.iops, .jobs[].write.lat_ns.mean'

  # sysbench
  echo "############# Sysbench ###################"
  cat $brd/sysbench.txt |egrep "max|\/sec"

done
