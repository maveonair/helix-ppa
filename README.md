# helix-debian

This repository contains the source to build a Debian package for [helix](https://github.com/helix-editor/helix)

## Usage

If you have [Docker](https://www.docker.com/) installed locally, just run the following:

```bash
$ ./build.sh
```
By default this will build helix 22.12 on Ubuntu LTS

If you want to customize the build at runtime, use the following:

```bash
$ ./build.sh -i ubuntu:22.10 -v 22.12
```
Don't forget to update `debian/changelog` so your package is generated with the correct version.

## Release

To publish a new package version to GitHub, follow these steps:
  * update the `VERSION` variable in `build.sh`
  * add a new entry in `debian/changelog`
  * create a new tag with the Debian package version

## Development

To improve the speed of local package creation, do the following:

```bash
$ docker build -t helix-debian -f Dockerfile.dev .
$ ./build.sh -i helix-debian
```

## References

* [barnumbirr/alacritty-debian](https://github.com/barnumbirr/alacritty-debian)
