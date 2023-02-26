#!/bin/env python3

import requests
import os
import subprocess
import sys
import tarfile

from shutil import move, rmtree
from contextlib import chdir
from distutils.dir_util import copy_tree


DEBIAN_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debian")
TARGET_DIRECTORY = os.path.join(os.getcwd(), "target")
HELIX_SOURCE_CODE_URL = "https://github.com/helix-editor/helix/archive/refs/tags"


def prepare_target(target_directory) -> None:
    rmtree(target_directory)
    os.mkdir(target_directory)


def get_args() -> tuple[str, str, str]:
    args = sys.argv[1:]

    if len(args) < 3:
        print(
            """
            Arguments are missing!

            Usage:
                ./build.py <helix-release> <ubuntu-codename> <changelog-version>

            Example:
                ./build.py 22.12 kinetic 22.12-5~ubuntu22.10~ppa1
            """
        )
        sys.exit(1)

    return args[0], args[1], args[2]


def get_helix_source_url(helix_version: str) -> str:
    return f"{HELIX_SOURCE_CODE_URL}/{helix_version}.tar.gz"


def download_helix_release(target_directory_path: str, helix_version: str) -> str:
    url = get_helix_source_url(helix_version)
    filename = f"helix_{helix_version}.orig.tar.gz"

    print(f"-> Downloading {url}...")
    response = requests.get(url, allow_redirects=True)

    target_file_path = os.path.join(target_directory_path, filename)

    with open(target_file_path, "wb") as file:
        file.write(response.content)

    return target_file_path


def unarchive_helix_release(target_directory_path: str, archive_file_path: str) -> None:
    with chdir(target_directory_path):
        print("-> Unarchive helix release...")
        with tarfile.open(archive_file_path) as tar:
            tar.extractall()


def prepare_debian_files(target_directory_path: str) -> str:
    debian_files_path = os.path.join(target_directory_path, "debian")

    print("-> Copy debian files")
    copy_tree(DEBIAN_DIRECTORY, debian_files_path)

    return debian_files_path


def create_cargo_vendor_archive(
    source_directory_path: str, destination_directory_path: str
) -> None:
    with chdir(source_directory_path):
        print("-> Run cargo vendor...")
        subprocess.check_call(["cargo", "vendor"])

        tar_file_path = os.path.join(destination_directory_path, "vendor.tar.xz")
        print(f"-> Create {tar_file_path}...")
        subprocess.check_call(["tar", "-czf", tar_file_path, "vendor/"])


def crate_grammar_sources_archive(
    source_directory_path: str, destination_directory_path: str
) -> None:
    with chdir(source_directory_path):
        print("-> Run cargo build...")
        subprocess.check_call(["cargo", "build", "--release"])

        tar_file_path = os.path.join(destination_directory_path, "grammars.src.tar.xz")
        print(f"-> Create {tar_file_path}...")
        subprocess.check_call(
            ["tar", "-czf", tar_file_path, "runtime/grammars/sources/"]
        )


def create_dependencies_archives(
    source_directory_path: str, destination_directory_path: str
) -> None:
    create_cargo_vendor_archive(
        source_directory_path=source_directory_path,
        destination_directory_path=destination_directory_path,
    )

    crate_grammar_sources_archive(
        source_directory_path=source_directory_path,
        destination_directory_path=destination_directory_path,
    )


def update_changelog(source_directory_path, ubuntu_codename, changelog_version) -> None:
    with chdir(source_directory_path):
        print("-> Create new changelog entry...")
        subprocess.check_call(
            [
                "dch",
                "--distribution",
                ubuntu_codename,
                "--package",
                "helix",
                "--newversion",
                changelog_version,
                f"No-change backport to {ubuntu_codename}",
            ]
        )


def prepare_for_build(
    target_directory: str,
    source_directory_path: str,
    helix_version: str,
) -> str:
    prepare_target(target_directory)

    release_file_path = download_helix_release(
        target_directory_path=target_directory, helix_version=helix_version
    )

    unarchive_helix_release(
        target_directory_path=target_directory, archive_file_path=release_file_path
    )

    debian_files_directory = prepare_debian_files(target_directory)

    create_dependencies_archives(
        source_directory_path=source_directory_path,
        destination_directory_path=debian_files_directory,
    )

    return release_file_path


def run_debuild(source_directory_path: str) -> None:
    with chdir(source_directory_path):
        print("-> Run debuild...")
        subprocess.check_call(["debuild", "-S", "-sa"])


def run_build(
    target_directory: str,
    source_directory_path: str,
    release_file_path: str,
    ubuntu_codename: str,
    changelog_version: str,
) -> None:
    prepare_target(source_directory_path)

    unarchive_helix_release(
        target_directory_path=target_directory, archive_file_path=release_file_path
    )

    move(os.path.join(target_directory, "debian"), source_directory_path)

    update_changelog(
        source_directory_path=source_directory_path,
        ubuntu_codename=ubuntu_codename,
        changelog_version=changelog_version,
    )

    run_debuild(source_directory_path)


def main():
    helix_version, ubuntu_codename, changelog_version = get_args()
    source_directory_path = os.path.join(TARGET_DIRECTORY, f"helix-{helix_version}")

    release_file_path = prepare_for_build(
        target_directory=TARGET_DIRECTORY,
        source_directory_path=source_directory_path,
        helix_version=helix_version,
    )

    run_build(
        target_directory=TARGET_DIRECTORY,
        source_directory_path=source_directory_path,
        release_file_path=release_file_path,
        ubuntu_codename=ubuntu_codename,
        changelog_version=changelog_version,
    )


if __name__ == "__main__":
    main()
