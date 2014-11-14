__author__ = 'panter.dsd@gmail.com'

import os
import sys
import subprocess


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
    return subprocess.check_output(["emerge", "--info"]).decode("utf-8").split("\n")


def extract_path(line: str) -> list:
    return line.strip('"').split(' ')


def emerge_value(key: str) -> str:
    value = str()

    for line in portage_env():
        if line.startswith(key + "="):
            value = line.split('=')[1]
            break

    return value


def manifests_folders() -> list:
    return extract_path(emerge_value("PORTDIR")) + extract_path(emerge_value("PORTDIR_OVERLAY"))


def load_file_names() -> list:
    file_names = []

    for folder_name in manifests_folders():
        file_names += load_files_from_manifests_folder(folder_name)

    return file_names


def distdir() -> str:
    return extract_path(emerge_value("DISTDIR"))[0]


def files_for_clean() -> dict:
    file_names = load_file_names()
    not_found_files = dict()
    distdir_path = distdir()

    for distdir_entry in os.listdir(distdir_path):
        full_entry_name = distdir_path + "/" + distdir_entry

        if not file_names.count(distdir_entry) and os.path.isfile(full_entry_name):
            not_found_files[full_entry_name] = os.path.getsize(full_entry_name)

    return not_found_files


def delete_files(files: list):
    for file_name in files:
        os.remove(file_name)


def main():
    files = files_for_clean()
    print(files)

    if sys.argv.count("--delete"):
        delete_files(files.keys())


if __name__ == '__main__':
    main()