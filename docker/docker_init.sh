#!/bin/bash
# Build the CLD image and extract default credentials.
set -e
IMAGE_NAME=cld-image
DATA_DIR=${1:-/var/cld}

docker build -t $IMAGE_NAME .
mkdir -p "$DATA_DIR"
# Use the container to populate default credentials and home dirs
# into the target directory.
docker run --rm -v "$DATA_DIR":/var/cld $IMAGE_NAME bash -c "/docker/init_creds.sh /var/cld"

echo "Credentials prepared under $DATA_DIR"

