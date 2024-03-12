#define Py_LIMITED_API 3
#include "Python.h"

#include <filesystem>

int main(int argc, char** argv) {
    std::filesystem::path exe_path = std::filesystem::path(argv[0]);
    std::filesystem::path bundle_root = exe_path.parent_path();

    std::wstring exe = exe_path.wstring();
    std::wstring app_main = (bundle_root / "app" / "main.py").wstring();
    std::wstring python_home = (bundle_root / "python").wstring();

#pragma warning(push)
#pragma warning(disable : 4996)
    // These two functions are deprecated since python 3.11.
    // However being part of the stable ABI they will continue to work.
    // See last paragraph of https://peps.python.org/pep-0652/#stable-abi
    // The worst case scenario is that they can end up leaking memory,
    // but that's not an issue here since they are only used once.
    Py_SetProgramName(exe.c_str());
    Py_SetPythonHome(python_home.c_str());
#pragma warning(pop)

    Py_Initialize();

    const int args_size = 4;
    wchar_t* args[] = {exe.data(),
                       L"-E", // Ignore PYTHON* environment variables.
                       L"-s", // Don't add user site directory to sys.path.
                       app_main.data()};

    // Don't pass the last argument if app/main.py doesn't exist.
    // In that case the interpreter will show its interactive prompt.
    Py_Main(std::filesystem::exists(app_main) ? args_size : 3, args);
}