#!/usr/bin/env bash
echo "Only run this script in the root of your code base."

bash CreateDockerfile.sh

echo "Remove container and images if exist... ..."
out=$(docker container stop mapf_test 2>&1 ; docker container rm mapf_test 2>&1 ; docker rmi mapf_image 2>&1)

echo "Build image and run the container... ..."

docker build --no-cache -t mapf_image ./

# check if gpu is available
if nvidia-smi &> /dev/null; then
    echo "GPU is available."
    docker container run -it --gpus all  --name mapf_test mapf_image
else
    echo "GPU is not available."
    docker container run -it --name mapf_test mapf_image
fi

