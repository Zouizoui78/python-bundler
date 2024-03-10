# python-bundler

This project's goal is to provide an easy way to bundler a python application into a package that can be executed by people who do not have the interpreter installed.

It is composed of two parts :

- A `python-launcher` cmake project that runs the python code in the [isolated interpreter](https://docs.python.org/3/c-api/init_config.html#c.PyConfig.isolated) included in the bundle. This project creates two executables :
  - `launcher.exe` is a normal Windows GUI-only program.
  - `launcher-console.exe` opens a terminal when running where logs can be seen.
- A python script called `bundler.py` that bundles a portable python interpreter, the target app and the wrapper.

This project is intended for Windows. Unix systems do not need this since they have proper package management systems.

`bundler.py` requires a working python install to get the targeted python version from and to get dependencies with pip.

## Build

Make sure you have python installed and available in the path. Then build the project :

    cmake -B build
    cmake --build build --target dist --config release

After that you get the archive `build/dist/python-bundler.zip` that contains the bundler script and the two versions of the launcher.

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

Here the python code is the one from the `test-app` example in this repo, without the dependencies on `tkinter` and `requests`.

We run the following command from `tmp` :

    python .\python-bundler\bundler.py --app .\test-app\ --launcher .\python-bundler\launcher-console.exe --output dist\bundle

We now have the following folder structure :

    tmp
    ├── dist
    │   ├── bundle // Our bundled package
    │   │   ├── app // Our python code
    │   │   ├── python // The portable python distribution
    │   │   └── test-app.exe // The renamed launcher-console.exe
    │   └── bundle.zip
    ├── python-bundler
    │   ├── bundler.py
    │   ├── launcher-console.exe
    │   └── launcher.exe
    └── test-app
        ├── lib.py
        └── main.py

We can then run `test-app.exe` from anywhere and it will run the python script `bundle/app/main.py` using the bundled python interpreter :

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
- If `app/main.py` does not exist and no CLI argument is provided, the launcher simply calls the interpreter's `main` function. If running the console launcher, you will simply get a python prompt.
- If `app/main.py` does not exist and a CLI argument is provided, it is used as the path to a script to execute.

## Dependencies

If the packaged application contains a file called `deps.json`, the list of string it
contains is used to get dependencies using pip. For instance, with the following json :

    [
        "tkinter",
        "requests"
    ]

`bundler.py` would install `tkinter` from the system python install and `requests` using `pip`.
