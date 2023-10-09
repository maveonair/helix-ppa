#!/bin/env python3

import argparse
import requests
import os
import subprocess
import sys
import tarfile

from shutil import move, rmtree
from contextlib import chdir
from shutil import copytree

parser = argparse.ArgumentParser(description="Build Helix for Ubuntu")
parser.add_argument("helix_version", type=str, help="Helix version to build")
parser.add_argument("ubuntu_codename", type=str, help="Ubuntu codename to build for")
parser.add_argument("changelog_version", type=str, help="Changelog version to use")
parser.add_argument("--skip-build", action="store_true", help="Skip the build step")

args = parser.parse_args()

DEBIAN_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debian")
TARGET_DIRECTORY = os.path.join(os.getcwd(), "target")
HELIX_SOURCE_CODE_URL = f"https://github.com/helix-editor/helix/releases/download/{args.helix_version}/helix-{args.helix_version}-source.tar.xz"


def prepare_target(target_directory: str) -> None:
    if os.path.exists(target_directory):
        rmtree(target_directory)

    os.mkdir(target_directory)


def download_helix_release(target_directory_path: str, helix_version: str) -> str:
    filename = f"helix_{helix_version}.orig.tar.xz"

    print(f"-> Downloading {HELIX_SOURCE_CODE_URL}...")
    response = requests.get(HELIX_SOURCE_CODE_URL, allow_redirects=True)

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
    copytree(DEBIAN_DIRECTORY, debian_files_path)

    return debian_files_path


def create_cargo_vendor_archive(
    source_directory_path: str, destination_directory_path: str
) -> None:
    with chdir(source_directory_path):
        print("-> Run cargo vendor...")
        subprocess.check_call(["cargo", "vendor"])

        tar_file_path = os.path.join(destination_directory_path, "vendor.tar.xz")
        print(f"-> Create {tar_file_path}...")
        subprocess.check_call(["tar", "cJf", tar_file_path, "vendor/"])


def create_dependencies_archives(
    source_directory_path: str, destination_directory_path: str
) -> None:
    create_cargo_vendor_archive(
        source_directory_path=source_directory_path,
        destination_directory_path=destination_directory_path,
    )


def prepare_for_build(helix_version: str, source_directory_path: str) -> str:
    prepare_target(TARGET_DIRECTORY)
    prepare_target(source_directory_path)

    release_file_path = download_helix_release(
        target_directory_path=TARGET_DIRECTORY,
        helix_version=helix_version,
    )

    unarchive_helix_release(
        target_directory_path=source_directory_path,
        archive_file_path=release_file_path,
    )

    debian_files_directory = prepare_debian_files(TARGET_DIRECTORY)

    create_dependencies_archives(
        source_directory_path=source_directory_path,
        destination_directory_path=debian_files_directory,
    )

    return release_file_path


def move_debian_files(source_directory_path: str, target_directory_path: str) -> None:
    move(source_directory_path, target_directory_path)


def update_changelog(source_directory_path, ubuntu_codename, changelog_version) -> None:
    with chdir(source_directory_path):
        print("-> Create new changelog entry...")
        subprocess.check_call(
            [
                "dch",
                "--force-bad-version",  # we use this because we use this script for back porting!
                "--distribution",
                ubuntu_codename,
                "--package",
                "helix",
                "--newversion",
                changelog_version,
                f"No-change backport to {ubuntu_codename}",
            ]
        )


def run_debuild(source_directory_path: str) -> None:
    with chdir(source_directory_path):
        print("-> Run debuild...")
        subprocess.check_call(["debuild", "--no-lintian", "-S", "-sa"])


def run_build(
    skip_build: bool,
    source_directory_path: str,
    release_file_path: str,
    ubuntu_codename: str,
    changelog_version: str,
) -> None:
    # We remove the extracted source directory because it contains
    # many compiled files from the prepare-for-build step that we
    # do not want in the final source archive.
    prepare_target(source_directory_path)

    unarchive_helix_release(
        target_directory_path=source_directory_path, archive_file_path=release_file_path
    )

    move_debian_files(
        source_directory_path=os.path.join(TARGET_DIRECTORY, "debian"),
        target_directory_path=source_directory_path,
    )

    if skip_build:
        return

    update_changelog(
        source_directory_path=source_directory_path,
        ubuntu_codename=ubuntu_codename,
        changelog_version=changelog_version,
    )

    run_debuild(source_directory_path)


def main():
    source_directory_path = os.path.join(
        TARGET_DIRECTORY, f"helix-{args.helix_version}"
    )

    release_file_path = prepare_for_build(
        helix_version=args.helix_version,
        source_directory_path=source_directory_path,
    )

    run_build(
        skip_build=args.skip_build,
        source_directory_path=source_directory_path,
        release_file_path=release_file_path,
        ubuntu_codename=args.ubuntu_codename,
        changelog_version=args.changelog_version,
    )


if __name__ == "__main__":
    main()
