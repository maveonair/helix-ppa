# helix-ppa

This repository contains the source which is used to build the Ubuntu package for [Helix](https://github.com/helix-editor/helix) and publish it to my personal PPA: [ppa:maveonair/helix-editor](https://launchpad.net/~maveonair/+archive/ubuntu/helix-editor)

## Release Process

### Build

```sh
$ ./build.py

Usage:
    ./build.py <ubuntu-codename> <changelog-version>

Example:
    ./build.py kinetic 23.03-2~ubuntu22.10~ppa1
```

### Example: Creating and publishing a new source package for Helix 23.03 on Ubuntu 22.10

1. Set `DEBMAIL` and `DEBFULLNAME`:

```sh
$ export DEBEMAIL="email@example.tld"
$ export DEBFULLNAME="Firstname Lastname"
```

2. Run build script:

```sh
$ ./build.py kinetic 23.03-2~ubuntu22.10~ppa1
```

3. Publish the source package

```sh
$ cd target
$ dput ppa:maveonair/helix-editor helix_23.03-2~ubuntu22.10~ppa1_source.changes
```

## References

- [barnumbirr/alacritty-debian](https://github.com/barnumbirr/alacritty-debian)
