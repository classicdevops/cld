#!/bin/bash
# Copy container credentials and home directories to the provided directory.
# Usage: ./docker/init_creds.sh [TARGET_DIR]
set -e
TARGET=${1:-/var/cld}

mkdir -p "$TARGET/docker/etc" "$TARGET/docker/home" "$TARGET/docker/root" "$TARGET/creds"

cp -a /etc/. "$TARGET/docker/etc/"
cp -a /home/. "$TARGET/docker/home/" 2>/dev/null || true
cp -a /root/. "$TARGET/docker/root/" 2>/dev/null || true

# prepare default credentials file
touch "$TARGET/creds/creds_static"
ln -sf creds_static "$TARGET/creds/creds"

echo "Credentials prepared under $TARGET/docker"
