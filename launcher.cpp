#define Py_LIMITED_API 3
#include "Python.h"

#include <filesystem>

int main(int argc, char** argv) {
    std::filesystem::path exe_path = std::filesystem::path(argv[0]);
    std::filesystem::path bundle_root = exe_path.parent_path();

    std::wstring exe = exe_path.wstring();
    std::wstring app_main = (bundle_root / "app" / "main.py").wstring();
    std::wstring python_home = (bundle_root / "python").wstring();

#if PY_MINOR_VERSION >= 11
// The two following functions are deprecated since Python 3.11.
// However being part of the stable ABI they will continue to work.
// See last paragraph of https://peps.python.org/pep-0652/#stable-abi
// The worst case scenario is that they can end up leaking memory,
// but that's not an issue here since they are only used once.
#pragma warning(push)
#pragma warning(disable : 4996)
#endif
    Py_SetProgramName(exe.data());
    Py_SetPythonHome(python_home.data());
#if PY_MINOR_VERSION >= 11
#pragma warning(pop)
#endif

    Py_Initialize();

    // Don't pass the last argument if app/main.py doesn't exist.
    // In that case the interpreter will show its interactive prompt.
    const int args_size = std::filesystem::exists(app_main) ? 4 : 3;
    wchar_t* args[] = {exe.data(),
                       L"-E", // Ignore PYTHON* environment variables.
                       L"-s", // Don't add user site directory to sys.path.
                       app_main.data()};

    Py_Main(args_size, args);
}