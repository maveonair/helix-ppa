# helix-ppa

This repository contains the source which is used to build the Debian package for [Helix](https://github.com/helix-editor/helix) and publish it to my personal PPA: [ppa:maveonair/helix-editor](https://launchpad.net/~maveonair/+archive/ubuntu/helix-editor)

## Release Process

### Build

```sh
$ ./build.py

Usage:
    ./build.py <helix-release> <ubuntu-codename> <changelog-version>

Example:
    ./build.py 22.12 kinetic 22.12-5~ubuntu22.10~ppa1
```

### Example: Creating and publishing a new source package for Helix 22.12 on Ubuntu 22.10

1. Set `DEBMAIL` and `DEBFULLNAME`:

```sh
$ export DEBEMAIL="email@example.tld"
$ export DEBFULLNAME="Firstname Lastname"
```

2. Run build script:

```sh
$ ./build.py 22.12 kinetic 22.12-5~ubuntu22.10~ppa1
```

3. Publish the source package

```sh
$ cd target/helix-22.12
$ dput ppa:maveonair/helix-editor helix_22.12-5~ubuntu22.10~ppa1_source.changes
```

## References

- [barnumbirr/alacritty-debian](https://github.com/barnumbirr/alacritty-debian)
