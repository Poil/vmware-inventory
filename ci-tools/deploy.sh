#!/bin/bash
docker ps -a|grep vmware-api
res=$?
if [[ ${res} -eq 0 ]]; then
    docker stop vmware-api
    docker rm vmware-api
fi
docker run -d -p 8003:8000 --restart=unless-stopped --name vmware-api vmware-api


