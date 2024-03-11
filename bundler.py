import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from urllib.request import urlretrieve

PYTHON_FULL_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
PYTHON_RELEASE = int(f"{sys.version_info.major}{sys.version_info.minor}")


def parse_args():
    argparser = argparse.ArgumentParser(
        description="Build the distributable package. If the packaged application contains a file called 'deps.json', the list of string it contains is used to get dependencies using pip."
    )
    argparser.add_argument(
        "-a",
        "--app",
        required=True,
        type=Path,
        help="Path to the application to package."
    )
    argparser.add_argument(
        "-l",
        "--launcher",
        required=True,
        type=Path,
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
    dlls_path = Path(os.path.join(python_path, "DLLs"))
    dlls_path.mkdir()

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
                os.path.join(Path(python_path).parent, file)
            )


def print_download_progress_bar(chunk_n: int, chunk_size: int, total_size: int):
    downloaded_size = chunk_n * chunk_size
    part_done = int(downloaded_size / total_size * 20)
    percent = part_done * 5
    left = 20 - part_done
    print(f"\r[{"#" * part_done}{" " * left}] ({percent}%)", end="")
    if left == 0:
        print()


def get_portable_python(python_path: str):
    python_url = f"https://www.python.org/ftp/python/{PYTHON_FULL_VERSION}/python-{PYTHON_FULL_VERSION}-embed-amd64.zip"
    print(f"Downloading '{python_url}'")
    python_zip = python_path + ".zip"
    urlretrieve(python_url, python_zip, reporthook=print_download_progress_bar)
    shutil.unpack_archive(python_zip, python_path)

    lib_zip = os.path.join(python_path, f"python{PYTHON_RELEASE}.zip")
    lib_path = os.path.join(python_path, f"Lib")
    shutil.unpack_archive(lib_zip, lib_path)

    os.remove(lib_zip)
    os.remove(python_zip)
    print("Download done\n")


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
    subprocess.check_call(args)


def get_dependencies(deps: list, python_path: str):
    print("Installing dependencies")
    for dep in deps:
        print(f"Installing {dep}")
        if dep == "tkinter":
            get_tkinter_from_system_python(python_path)
        else:
            site_packages_path = Path(os.path.join(python_path, "Lib/site-packages"))
            site_packages_path.mkdir(parents=True, exist_ok=True)
            get_dep_from_pypi(dep, site_packages_path)
        print()
    print("Done installing dependencies")


def main():
    args = parse_args()

    if args.name != None:
        app_name = args.name
    elif args.output != None:
        app_name = os.path.basename(args.output)
    else:
        app_name = os.path.basename(args.app)

    if args.output == None:
        output_dir = Path(f"bundle/{app_name}")
    else:
        output_dir = Path(args.output)

    print()
    print(f"Bundling python app '{app_name}'")
    print(f"source directory = {args.app}")
    print(f"destination directory = {output_dir}")
    print()

    shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    python_path = os.path.join(output_dir, "python")
    get_portable_python(python_path)

    shutil.copytree(
        args.app,
        os.path.join(output_dir, "app"),
        ignore=shutil.ignore_patterns("__pycache__", "deps.json")
    )
    print(f"Copied '{args.app}' to '{output_dir}'")
    shutil.copy(args.launcher, os.path.join(output_dir, app_name + ".exe"))
    print(f"Copied '{args.launcher}' to '{output_dir}'")
    print()

    deps_path = os.path.join(args.app, "deps.json")
    if os.path.exists(deps_path):
        with open(deps_path, "r") as f:
            get_dependencies(json.load(f), python_path)

    cleanup_python_install(python_path)

    print()
    print(f"Creating archive '{output_dir}.zip'")
    shutil.make_archive(output_dir, "zip", root_dir=output_dir.parent, base_dir=output_dir.name)
    print("Done")


if __name__ == "__main__":
    main()