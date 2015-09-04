#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'panter.dsd@gmail.com'

import os
import sys
import subprocess

import humansize


def extract_file_name(manifest_string: str) -> str:
    prefix = "DIST "
    if not manifest_string.startswith(prefix):
        return str()

    end = manifest_string.find(' ', len(prefix))
    return manifest_string[len(prefix):end] if end > 0 else str()


def load_files_from_manifest(manifest_file_name: str) -> iter:
    print("Parse " + manifest_file_name)

    with open(manifest_file_name, "r") as file:
        file_names = (extract_file_name(line) for line in file.readlines())
        return (file_name for file_name in file_names if file_name)


def __manifest_files(files: list):
    return (file_name for file_name in files if file_name == "Manifest")


def load_files_from_manifests_folder(folder_name: str) -> iter:
    for root, _, files in os.walk(folder_name):
        for file_name in __manifest_files(files):
            for name in load_files_from_manifest(root + "/" + file_name):
                yield name


def portage_env() -> list:
    if not hasattr(portage_env, "cache"):
        portage_env.cache = subprocess.check_output(["emerge", "--info"]).decode("utf-8").split("\n")
    return portage_env.cache


def extract_path(line: str) -> list:
    return line.strip('"').split(' ') if line else list()


def emerge_value(key: str) -> str:
    if not hasattr(emerge_value, "values"):
        key_value_lines = (line for line in portage_env() if line.count("=") == 1)
        key_value = (line.split('=') for line in key_value_lines)
        emerge_value.values = {k: v for k, v in key_value}

    try:
        return emerge_value.values[key]
    except KeyError:
        return str()


def old_portage_manifest_folders() -> list:
    return extract_path(emerge_value("PORTDIR")) + extract_path(emerge_value("PORTDIR_OVERLAY"))


def new_portage_manifest_folders() -> list:
    return [line.strip().split(' ')[1] for line in portage_env() if "location: " in line]


def manifests_folders() -> list:
    return old_portage_manifest_folders() or new_portage_manifest_folders()


def load_file_names() -> iter:
    for folder_name in manifests_folders():
        for file_name in load_files_from_manifests_folder(folder_name):
            yield file_name


def distdir() -> str:
    return extract_path(emerge_value("DISTDIR"))[0]


def __remove(container: set, entry: str):
    try:
        container.remove(entry)
        return True
    except KeyError:
        return False


def __files_not_in_container(path: str, container: set) -> iter:
    for file_name in os.listdir(path):
        full_file_name = path + "/" + file_name
        if not __remove(container, file_name) and os.path.isfile(full_file_name):
            yield full_file_name


def files_for_clean() -> dict:
    file_names = set(load_file_names())

    return {
        file_name: os.path.getsize(file_name) for file_name in __files_not_in_container(distdir(), file_names)
        } if file_names else dict()


def delete_files(files: iter):
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
