import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from urllib.request import urlretrieve

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
        help="Path to the output directory."
    )
    argparser.add_argument(
        "-n",
        "--name",
        help="Name of the application. Defaults to the name of the app directory."
    )
    return argparser.parse_args()

def get_python(python_full_version: str, python_release: str, python_path: str):
    python_url = f"https://www.python.org/ftp/python/{python_full_version}/python-{python_full_version}-embed-amd64.zip"
    python_zip = python_path + ".zip"
    urlretrieve(python_url, python_zip)
    shutil.unpack_archive(python_zip, python_path)

    lib_zip = os.path.join(python_path, f"python{python_release}.zip")
    lib_path = os.path.join(python_path, f"Lib")
    shutil.unpack_archive(lib_zip, lib_path)

    os.remove(lib_zip)
    os.remove(python_zip)

def get_tkinter(python_path: str):
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
    shutil.copy(os.path.join(python_dlls_path, "zlib1.dll"), python_path)

def get_pypi_dep(dep_name: str, site_packages_path: str):
    args = [sys.executable, "-m", "pip", "install", dep_name, "--target", site_packages_path]
    subprocess.check_call(args)

def get_deps(deps: list, python_path: str):
    for dep in deps:
        if dep == "tkinter":
            get_tkinter(python_path)
        else:
            site_packages_path = Path(os.path.join(python_path, "Lib/site-packages"))
            site_packages_path.mkdir(parents=True, exist_ok=True)
            get_pypi_dep(dep, site_packages_path)

def main():
    args = parse_args()

    if args.name == None:
        app_name = os.path.basename(args.app)
    else:
        app_name = args.name

    if args.output == None:
        output_dir = Path("bundle")
    else:
        output_dir = Path(args.output)

    shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    python_full_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    python_release = f"{sys.version_info.major}{sys.version_info.minor}"
    python_path = os.path.join(output_dir, "python")
    get_python(python_full_version, python_release, python_path)

    shutil.copytree(args.app, os.path.join(output_dir, "app"), ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(args.launcher, os.path.join(output_dir, app_name + ".exe"))

    deps_path = os.path.join(args.app, "deps.json")
    if os.path.exists(deps_path):
        with open(deps_path, "r") as f:
            get_deps(json.load(f), python_path)

    print(output_dir)
    shutil.make_archive(output_dir, "zip", root_dir=output_dir.parent, base_dir=output_dir.name)

if __name__ == "__main__":
    main()