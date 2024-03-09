# python-launcher

Simply bundle a python application to make it usable by user who do not have the interpreter installed.

This project is built for Windows. Unix systems do not need this since they have proper dependency management systems.

The script requires a working python install to get the targeted python version from and to get dependencies with pip.

## How to use

1. Make sure you have python installed and available in the path.
2. Build the project.
3. Run the dist.py script.

## What does the launcher executes

There are three cases:

- If the app directory contains a `main.py` file, it is executed.
- If the app directory contains no `main.py` file and no CLI argument is provided, the launcher simply calls the interpreter's `main` function. If running the console launcher, you will simply get a python prompt.
- If the app directory contains no `main.py` file and a CLI argument is provided, it is used as the path to a script to execute.

## Difference between the two launchers

When building the project, you get two launcher : `python-launcher.exe` and `python-launcher-console.exe`. The latter opens a terminal when running.

## Dependencies

If the packaged application contains a file called `deps.json`, the list of string it
contains is used to get dependencies using pip. For example with the following json :

    [
        "tkinter",
        "requests"
    ]

`dist.py` would install `tkinter` from the system python install and `requests` using `pip`.

## Build

    cmake -B build
    cmake --build build --target dist --config release
