import argparse
import json
import os
import shutil
import subprocess
import sys
from urllib.request import urlretrieve

PYTHON_FULL_VERSION = "{}.{}.{}".format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
PYTHON_RELEASE = int("{}{}".format(sys.version_info.major, sys.version_info.minor))

CACHE_DIR = os.path.join(os.path.dirname(sys.argv[0]), ".python-bundler-cache")
CACHED_PYTHON_ZIP = os.path.join(CACHE_DIR, "python{}.zip".format(PYTHON_RELEASE))


def parse_args():
    argparser = argparse.ArgumentParser(
        description="Build the distributable package. If the packaged application contains a file called 'deps.json', the list of string it contains is used to get dependencies using pip."
    )
    argparser.add_argument(
        "-a",
        "--app",
        required=True,
        help="Path to the application to package."
    )
    argparser.add_argument(
        "-l",
        "--launcher",
        required=True,
        help="Launcher to package into the distribution."
    )
    argparser.add_argument(
        "-o",
        "--output",
        help="Path to the output directory. Defaults to 'bundle'."
    )
    argparser.add_argument(
        "-n",
        "--name",
        help="Name of the application. Defaults to the name of the app directory, or, if set, to the name of the output directory."
    )
    return argparser.parse_args()


def file_belongs_in_dlls_dir(file: str) -> bool:
    return file.endswith(".pyd") or \
        file.endswith(".dll") and \
        "python" not in file and \
        "vcruntime" not in file


def cleanup_python_install(python_path: str):
    extensions_to_remove = [".exe", ".cat", "._pth"]
    dlls_path = os.path.join(python_path, "DLLs")
    os.makedirs(dlls_path, exist_ok=True)

    for file in os.listdir(python_path):
        file_path = os.path.join(python_path, file)
        if file_belongs_in_dlls_dir(file):
            os.rename(
                file_path,
                os.path.join(dlls_path, file)
            )
        elif any([file.endswith(ext) for ext in extensions_to_remove]):
            os.remove(file_path)
        elif file.endswith(".dll"):
            os.rename(
                file_path,
                os.path.join(python_path, os.pardir, file)
            )


def print_download_progress_bar(chunk_n: int, chunk_size: int, total_size: int):
    downloaded_size = chunk_n * chunk_size
    part_done = int(downloaded_size / total_size * 20)
    percent = part_done * 5
    left = 20 - part_done
    print("\r[{}{}] ({}%)".format('#' * part_done, ' ' * left, percent), end="")
    if left == 0:
        print()


def download_python():
    python_url = "https://www.python.org/ftp/python/{}/python-{}-embed-amd64.zip".format(PYTHON_FULL_VERSION, PYTHON_FULL_VERSION)
    print("Downloading '{}' to '{}'".format(python_url, CACHED_PYTHON_ZIP))
    urlretrieve(python_url, CACHED_PYTHON_ZIP, reporthook=print_download_progress_bar)


def get_portable_python(python_path: str):
    if not os.path.exists(CACHED_PYTHON_ZIP):
        os.makedirs(CACHE_DIR, exist_ok=True)
        download_python()
    else:
        print("Using cached {}".format(CACHED_PYTHON_ZIP))
    shutil.unpack_archive(CACHED_PYTHON_ZIP, python_path)

    lib_zip = os.path.join(python_path, "python{}.zip".format(PYTHON_RELEASE))
    lib_path = os.path.join(python_path, "Lib")
    shutil.unpack_archive(lib_zip, lib_path)

    os.remove(lib_zip)


def get_tkinter_from_system_python(python_path: str):
    python_install_path = sys.exec_prefix
    python_dlls_path = os.path.join(python_install_path, "DLLs")
    shutil.copytree(
        os.path.join(python_install_path, "tcl"),
        os.path.join(python_path, "tcl"),
        ignore=shutil.ignore_patterns("__pycache__")
    )
    shutil.copytree(
        os.path.join(python_install_path, "Lib", "tkinter"),
        os.path.join(python_path, "tkinter"),
        ignore=shutil.ignore_patterns("__pycache__")
    )
    shutil.copy(os.path.join(python_dlls_path, "_tkinter.pyd"), python_path)
    shutil.copy(os.path.join(python_dlls_path, "tcl86t.dll"), python_path)
    shutil.copy(os.path.join(python_dlls_path, "tk86t.dll"), python_path)

    if PYTHON_RELEASE >= 312:
        shutil.copy(os.path.join(python_dlls_path, "zlib1.dll"), python_path)


def get_dep_from_pypi(dep_name: str, site_packages_path: str):
    args = [sys.executable, "-m", "pip", "install", dep_name, "--target", site_packages_path]
    subprocess.call(args)


def get_dependencies(deps: list, python_path: str):
    print("Installing dependencies")
    for dep in deps:
        print("Installing {}".format(dep))
        if dep == "tkinter":
            get_tkinter_from_system_python(python_path)
        else:
            site_packages_path = os.path.join(python_path, "Lib/site-packages")
            os.makedirs(site_packages_path, exist_ok=True)
            get_dep_from_pypi(dep, site_packages_path)
        print()
    print("Done installing dependencies")
    print()


def main():
    args = parse_args()

    # Remove trailing dir separator
    # Otherwise basename returns '' for python < 3.6
    if (args.app[-1] == os.sep):
        args.app = args.app[:-1]

    if args.name != None:
        app_name = args.name
    elif args.output != None:
        app_name = os.path.basename(args.output)
    else:
        app_name = os.path.basename(args.app)

    if args.output == None:
        output_dir = "bundle/{}".format(app_name)
    else:
        output_dir = args.output

    print()
    print("Bundling python app '{}'".format(app_name))
    print("source directory = {}".format(args.app))
    print("destination directory = {}".format(output_dir))
    print()

    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir)

    python_path = os.path.join(output_dir, "python")
    get_portable_python(python_path)

    shutil.copytree(
        args.app,
        os.path.join(output_dir, "app"),
        ignore=shutil.ignore_patterns("__pycache__", "deps.json")
    )
    print("Copied '{}' to '{}'".format(args.app, output_dir))
    shutil.copy(args.launcher, os.path.join(output_dir, app_name + ".exe"))
    print("Copied '{}' to '{}'".format(args.launcher, output_dir))
    print()

    deps_path = os.path.join(args.app, "deps.json")
    if os.path.exists(deps_path):
        with open(deps_path, "r") as f:
            get_dependencies(json.load(f), python_path)

    cleanup_python_install(python_path)

    print("Creating archive '{}.zip'".format(output_dir))
    shutil.make_archive(
        output_dir,
        "zip",
        root_dir=os.path.join(output_dir, os.pardir),
        base_dir=os.path.basename(output_dir)
    )
    print("Done")


if __name__ == "__main__":
    main()