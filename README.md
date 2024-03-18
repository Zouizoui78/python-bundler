# python-bundler

This project's goal is to provide an easy way to bundle a Python application into a package that can be executed by people who do not have the interpreter installed.

It is composed of two parts :

- The C++ project `python-launcher` that runs the Python code in a portable interpreter included in the bundle. This project creates two executables :
  - `launcher.exe` is a normal Windows GUI-only program.
  - `launcher-console.exe` is a console program.
- The Python script `bundler.py` that bundles the portable Python interpreter, the target app and the C++ wrapper.

The launcher uses Python's [stable ABI](https://docs.python.org/3/c-api/stable.html#stable-abi) so it should work with all versions of Python 3.x >= 3.2 (when the stable ABI was introduced).

This project is intended for Windows. Unix systems do not need this since they have proper package management systems.

## Requirements

- Python >= 3.5 installed and available in the path

The Python version requirement comes from the fact that Python didn't ship an embeddable distribution before 3.5.

## How to use

Download the bundler from the [releases](https://github.com/Zouizoui78/python-bundler/releases/latest) and extract the files somewhere.

Let's consider the following folder structure as an example. The `test-app` is the one from the root of this project.

    tmp
    ├── python-bundler
    │   ├── bundler.py
    │   ├── launcher-console.exe
    │   └── launcher.exe
    └── test-app
        ├── deps.json
        ├── lib.py
        └── main.py

We run the following command from `tmp` :

    python .\python-bundler\bundler.py --app .\test-app\ --launcher .\python-bundler\launcher-console.exe

We now have the following folder structure :

    tmp
    ├── bundle
    │   ├── test-app // Our bundled package
    │   │   ├── app // Our python code
    │   │   ├── python // The portable python distribution
    │   │   ├── test-app.exe // The launcher (renamed)
    │   │   └── <some DLLs>
    │   └── test-app.zip // The zipped bundle
    ├── python-bundler
    │   ├── bundler.py
    │   ├── launcher-console.exe
    │   └── launcher.exe
    └── test-app
        ├── deps.json
        ├── lib.py
        └── main.py

We can then run `test-app.exe` from anywhere and it will run the Python script `bundle/test-app/app/main.py` using the bundled Python interpreter :

    .\bundle\test-app\test-app.exe

The script should output some text telling about Python's paths.

An icon can also be added to the launcher with the `--icon` flag of `bundler.py`.

See `bundler.py -h` for more information.

### Dependencies

If the packaged application contains a file called `deps.json`, the list of strings it
contains is used to get dependencies using `pip`. For instance, with the following json :

    [
        "tkinter",
        "requests"
    ]

`bundler.py` would install `tkinter` from the system Python install and `requests` using `pip`.

## What does the launcher execute

- If `app/main.py` exists, it is executed.
- If `app/main.py` does not exist, the launcher calls the interpreter's `main` function. If running the console launcher, you will get a Python prompt.

## Build

You need the following to build the wrapper :

- MSVC
- CMake >= 3.26 for the `Development.SABIModule` component of `FindPython`
- Python >= 3.2 for the stable ABI

Clone and build the project :

    git clone https://github.com/Zouizoui78/python-bundler.git
    cd python-bundler
    cmake -B build
    cmake --build build --target dist --config release

The `dist` target creates the archive `build/dist/python-bundler.zip` that contains the bundler script and the two versions of the launcher.
