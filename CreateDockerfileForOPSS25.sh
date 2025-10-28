#!/usr/bin/env bash
echo "Only run this script in the root of your code base."
echo "Create Dockerfile using apt.txt"

if [ $# -eq 0 ]
  then
      base_image="pytorch/pytorch:2.4.1-cuda11.8-cudnn9-devel"
      echo "Using default base image: $base_image"
   else
      base_image=$1
      echo "Using base image: $base_image"
fi


# Specify which docker to use.
content="FROM ${base_image}\nRUN apt-get update\n"


# Read packages to install.
pkgs='RUN ["apt-get", "install", "--yes", "--no-install-recommends"'
while read -r line;
do
   pkgs="${pkgs},\"$line\"" ;
done < apt.txt
pkgs="${pkgs}]\n"
content="${content}${pkgs}"

content="${content}RUN python3 -m pip install --upgrade --no-cache-dir pip setuptools wheel \n"

# Copy codes to target dir and set codes dir to be the working directory.
# Then run compile.sh to compile codes.
content="${content}COPY ./. /MAPF/codes/ \n"
content="${content}WORKDIR /MAPF/codes/ \n"

content="${content}RUN python3 -m pip install -r pip.txt\n"

content="${content}RUN rm -rdf /MAPF/codes/build \n"
content="${content}RUN chmod u+x compile-opss25.sh \n"

content="${content}RUN ./compile-opss25.sh \n"

content="${content}CMD [\"/MAPF/codes/build/lifelong\"]\n"

echo -e $content > Dockerfile