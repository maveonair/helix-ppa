#!/bin/bash

set -eu

IMAGE="ubuntu:22.04"
TARGET="$(dirname "$0" | xargs realpath)"
VERSION="22.12"

while getopts "v:i:h" opt
do
    case "$opt" in
        v)
            VERSION="$OPTARG"
            ;;
        i)
            IMAGE="$OPTARG"
            ;;
        h)
            echo "Usage: $0 [-i image] [-v version]"
            exit 0
            ;;
        *)
            exit 1
            ;;
    esac
done

main() {
    docker run --rm --name helix-build-$$ \
                    --platform linux/amd64 \
                    --volume "$TARGET:/target" \
                    --workdir /target \
                    --env "VERSION=$VERSION" \
                    --user root "$IMAGE" \
                    sh entrypoint.sh
}

main
