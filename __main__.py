#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'panter.dsd@gmail.com'

import os
import sys
import subprocess
import humansize
import re


def extract_file_name(manifest_string: str) -> str:
    return manifest_string.split(' ', 2)[1] \
        if manifest_string.startswith("DIST") and manifest_string.count(' ') > 2 \
        else str()


def load_files_from_manifest(manifest_file_name: str) -> list:
    print("Parse " + manifest_file_name)

    file_names = []

    with open(manifest_file_name, "r") as file:
        for line in file.readlines():
            file_name = extract_file_name(line)
            if file_name:
                file_names.append(file_name)

    return file_names


def load_files_from_manifests_folder(folder_name: str) -> list:
    file_names = []

    for root, subFolders, files in os.walk(folder_name):
        for file_name in files:
            if file_name == "Manifest":
                file_names += load_files_from_manifest(root + "/" + file_name)

    return file_names


def portage_env() -> list:
    if not hasattr(portage_env, "cache"):
        portage_env.cache = subprocess.check_output(["emerge", "--info"]).decode("utf-8").split("\n")
    return portage_env.cache


def extract_path(line: str) -> list:
    return line.strip('"').split(' ') if line else list()


def emerge_value(key: str) -> str:
    value = str()

    for line in portage_env():
        if line.startswith(key + "="):
            value = line.split('=')[1]
            break

    return value


def old_portage_manifest_folders() -> list:
    return extract_path(emerge_value("PORTDIR")) + extract_path(emerge_value("PORTDIR_OVERLAY"))

def new_portage_manifest_folders() -> list:
    path_regexp = re.compile("\s*location: (.*)")

    result = []
    for line in portage_env():
        match = path_regexp.match(line)
        if match:
            result.append(match.group(1))

    return result

def manifests_folders() -> list:
    result = old_portage_manifest_folders()
    return result if result else new_portage_manifest_folders()


def load_file_names() -> list:
    file_names = []

    for folder_name in manifests_folders():
        file_names += load_files_from_manifests_folder(folder_name)

    if not file_names:
        print("Not found manifests")

    return file_names


def distdir() -> str:
    return extract_path(emerge_value("DISTDIR"))[0]


def files_for_clean() -> dict:
    file_names = load_file_names()
    if not file_names:
        return dict()
    
    not_found_files = dict()
    distdir_path = distdir()

    for distdir_entry in os.listdir(distdir_path):
        full_entry_name = distdir_path + "/" + distdir_entry

        not_found = False
        try:
            file_names.remove(distdir_entry)
        except ValueError:
            not_found = True

        if not_found and os.path.isfile(full_entry_name):
            not_found_files[full_entry_name] = os.path.getsize(full_entry_name)

    return not_found_files


def delete_files(files: list):
    for file_name in files:
        os.remove(file_name)


def print_result(files: dict):
    total_size = 0
    for key, value in files.items():
        print("[ {:>10} ] {}".format(humansize.approximate_size(value), key))
        total_size += value
    print("==========================================================================================")
    print("[ {:>10} ] Total size".format(humansize.approximate_size(total_size)))


def main():
    files = files_for_clean()
    print_result(files)

    if sys.argv.count("--delete"):
        delete_files(files.keys())


if __name__ == '__main__':
    main()
    sys.exit(0)
