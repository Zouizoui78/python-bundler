#define Py_LIMITED_API 3
#include "Python.h"

#include <filesystem>
#include <vector>

#include <windows.h> // For MultiByteToWideChar()

std::wstring str_to_wstring(const char* str) {
    int len = static_cast<int>(strlen(str));
    std::wstring ret;
    ret.resize(len);
    int ret_len = static_cast<int>(ret.size());

    int convert_result =
        MultiByteToWideChar(CP_UTF8, 0, str, len, ret.data(), ret_len);
    if (convert_result <= 0) {
        throw std::exception("Failed to convert an argument to unicode");
    }
    return ret;
}

int main(int argc, char** argv) {
    std::filesystem::path bundle_root =
        std::filesystem::path(argv[0]).parent_path();

    std::wstring app_main = (bundle_root / "app" / "main.py").wstring();
    std::wstring python_home = (bundle_root / "python").wstring();

#if PY_MINOR_VERSION >= 11
// Py_SetPythonHome() is deprecated since Python 3.11.
// However being part of the stable ABI it will continue to work.
// See last paragraph of https://peps.python.org/pep-0652/#stable-abi
// The worst case scenario is that it can end up leaking memory,
// but that's not an issue here since it is only used once.
#pragma warning(push)
#pragma warning(disable : 4996)
#endif
    Py_SetPythonHome(python_home.data());
#if PY_MINOR_VERSION >= 11
#pragma warning(pop)
#endif

    std::vector<std::wstring> args_storage{
        L"-E", // Ignore PYTHON* environment variables.
        L"-s"  // Don't add user site directory to sys.path.
    };

    if (std::filesystem::exists(app_main)) {
        args_storage.emplace_back(app_main);
        for (int i = 1; i < argc; i++) {
            args_storage.emplace_back(str_to_wstring(argv[i]));
        }
    }

    std::vector<wchar_t*> args;
    for (auto& str : args_storage) {
        args.emplace_back(str.data());
    }

    Py_Initialize();
    Py_Main(static_cast<int>(args.size()), args.data());
}