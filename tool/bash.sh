#!/bin/bash
for consumer_group in `/opt/bitnami/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list`
  do
    for info in `/opt/bitnami/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group $consumer_group | tail -n +3 | awk '{print $1","$2","$9}'`
      do
        echo $info
      done
  done