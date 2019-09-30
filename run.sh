#!/bin/bash
show_help()
{
    echo ------------------------------------------------------------------
    echo Runs "arturol76/ddns" on the target "docker-ip" host.
    echo Container name is specified by "container_name".
    echo
    echo NOTE: it will create and mount a named volume '${container_name}_cfg'
    echo for the persistent storage of config files.
    echo
    echo USAGE:
    echo ./run.sh docker_ip container_name repo_tag
    echo
    echo EXAMPLE:
    echo ./run.sh 192.168.2.96 ddns-test latest
    echo ./run.sh 192.168.2.96 ddns-test test
    echo ------------------------------------------------------------------
    echo
}

num_of_params=3
docker_host=$1
container_name=$2
repo_tag=$3

#checks number of parameters
if [ "$#" -ne $num_of_params ]; then
    echo "Illegal number of parameters."
    echo
    show_help
    exit 1
fi

#EDIT TO YOUR NEEDS--------------------
docker_image=arturol76/ddns:$repo_tag
#--------------------------------------

echo creating volumes...
volume_cfg=${container_name}_cfg
docker -H $docker_host volume create ${volume_cfg}

read -p "Do you want to pull image? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo
    echo pulling image...
    docker -H $docker_host pull $docker_image
else 
    echo
fi

if [ "$(docker -H $docker_host ps -a | grep $container_name)" ]; then
    echo container $container_name already exists

    echo stopping it...
    docker -H $docker_host stop $container_name

    echo removing it...
    docker -H $docker_host rm $container_name
fi

# create your container
echo creating the container...
docker -H $docker_host create \
    -it \
    --restart always \
    --name $container_name \
    --env-file "./secrets/vars.env" \
    -e TZ="Europe/Rome" \
    -v ${volume_cfg}:/app/conf \
    $docker_image

#copy config files into container
if true; then
    read -p "Do you want to init volumes with config files? " -n 1 -r
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        echo
        
        #copy config files into container
        echo copying files into container...
        docker -H $docker_host cp ./secrets/config.json $container_name:/app/conf/config.json
    else
        echo
    fi
fi

#run
echo starting the container...
docker -H $docker_host start \
    $container_name

exit 0