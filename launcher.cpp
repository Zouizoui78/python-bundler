#define Py_LIMITED_API 3
#include <Python.h>

#include <filesystem>
#include <iostream>

int main(int argc, char** argv) {
    auto exe = std::filesystem::path(argv[0]);
    auto bundle_root = exe.parent_path();
    auto app_root = bundle_root / "app";
    auto app_main = app_root / "main.py";
    auto python_home = bundle_root / "python";
    auto python_dlls = python_home / "DLLs";
    auto python_lib = python_home / "Lib";

    auto exe_str = exe.wstring();
    auto app_main_str = app_main.wstring();
    auto python_home_str = python_home.wstring();

#pragma warning(push)
#pragma warning(disable : 4996)
    Py_SetProgramName(exe_str.c_str());
    Py_SetPythonHome(python_home_str.c_str());
#pragma warning(pop)

    Py_Initialize();

    const int args_size = 4;
    wchar_t* args[args_size] = {exe_str.data(), L"-E", L"-s",
                                app_main_str.data()};

    Py_Main(args_size, args);
}