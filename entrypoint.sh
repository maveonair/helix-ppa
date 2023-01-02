#!/bin/bash

set -xeu

BRANCH="$VERSION"
DEBIAN_FRONTEND=noninteractive
DEB_BUILD_OPTIONS=parallel=$(nproc)
TARGET="$PWD"

export DEBIAN_FRONTEND DEB_BUILD_OPTIONS

dependencies() {
    apt-get update && apt-get install -y devscripts equivs git
}

get_sources() {
    cd "$(mktemp -d)"
    git clone -b "$BRANCH" https://github.com/helix-editor/helix.git helix
    cd helix
}

build() {
    cp -a "$TARGET/debian" .
    yes | mk-build-deps --install
    dpkg-source --before-build .
    debian/rules build
    debian/rules binary
}

copy() {
    TARGET_UID="$(stat --printf %u "$TARGET")"
    TARGET_GID="$(stat --printf %g "$TARGET")"
    install -o "$TARGET_UID" -g "$TARGET_GID" -t "$TARGET/target" ../*.deb
}

main() {
    dependencies
    get_sources
    build
    copy
}

main
