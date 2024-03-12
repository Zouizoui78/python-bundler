# python-bundler

This project's goal is to provide an easy way to bundle a Python application into a package that can be executed by people who do not have the interpreter installed.

It is composed of two parts :

- A `python-launcher` cmake project that runs the Python code in an [isolated interpreter](https://docs.python.org/3/c-api/init_config.html#c.PyConfig.isolated) included in the bundle. This project creates two executables :
  - `launcher.exe` is a normal Windows GUI-only program.
  - `launcher-console.exe` opens a terminal when running where logs can be seen.
- A Python script called `bundler.py` that bundles a portable Python interpreter, the target app and the C++ wrapper.

The launcher use Python's [stable abi](https://docs.python.org/3/c-api/stable.html#stable-abi) so it should work with all versions of Python >= 3.2.

This project is intended for Windows. Unix systems do not need this since they have proper package management systems.

`bundler.py` requires a working Python >= 3.5 install to get the targeted Python version from and to get dependencies with pip. The version requirement comes from the fact that Python didn't ship an embeddable distribution before 3.5.

## How to use

Consider the following folder structure :

    tmp
    ├── python-bundler
    │   ├── bundler.py
    │   ├── launcher-console.exe
    │   └── launcher.exe
    └── test-app
        ├── lib.py
        └── main.py

Here the Python code is the one from the `test-app` example of this repo, without the dependencies on `tkinter` and `requests`.

We run the following command from `tmp` :

    python .\python-bundler\bundler.py --app .\test-app\ --launcher .\python-bundler\launcher-console.exe

We now have the following folder structure :

    tmp
    ├── bundle // Our bundled package
    │   ├── app // Our python code
    │   ├── python // The portable python distribution
    │   ├── python312.dll
    │   ├── python3.dll
    │   ├── test-app.exe // The launcher (renamed)
    │   ├── vcruntime140_1.dll
    │   └── vcruntime140.dll
    ├── bundle.zip
    ├── python-bundler
    │   ├── bundler.py
    │   ├── launcher-console.exe
    │   └── launcher.exe
    └── test-app
        ├── lib.py
        └── main.py

We can then run `test-app.exe` from anywhere and it will run the Python script `bundle/app/main.py` using the bundled Python interpreter :

    tmp> .\dist\bundle\test-app.exe
    hi from lib
    __file__ = C:\dev\tmp\dist\bundle\app\main.py
    sys.path = [
        C:\dev\tmp\dist\bundle\python\Lib,
        C:\dev\tmp\dist\bundle\app,
        C:\dev\tmp\dist\bundle\python,
        C:\dev\tmp\dist\bundle\python\Lib\site-packages
    ]
    prefix = C:\dev\tmp\dist\bundle\python
    executable = C:\dev\tmp\dist\bundle\test-app.exe
    site-packages = [
        C:\dev\tmp\dist\bundle\python,
        C:\dev\tmp\dist\bundle\python\Lib\site-packages
    ]

## What does the launcher executes

There are three cases:

- If `app/main.py` exists, it is executed.
- If `app/main.py` does not exist, the launcher calls the interpreter's `main` function. If running the console launcher, you will get a Python prompt.

## Dependencies

If the packaged application contains a file called `deps.json`, the list of string it
contains is used to get dependencies using pip. For instance, with the following json :

    [
        "tkinter",
        "requests"
    ]

`bundler.py` would install `tkinter` from the system Python install and `requests` using `pip`.

## Build

You need the following to build the wrapper :

- MSVC with support for C++17 for `std::filesystem`
- CMake >= 3.5
- Python >= 3.2 for the stable ABI

Clone and build the project :

    git clone https://github.com/Zouizoui78/python-bundler.git
    cd python-launcher
    cmake -B build
    cmake --build build --target dist --config release

The `dist` target creates the archive `build/dist/python-bundler.zip` that contains the bundler script and the two versions of the launcher.
