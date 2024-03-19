#define Py_LIMITED_API 3
#include "Python.h"

#include <windows.h> // For MultiByteToWideChar()

enum ReturnCodes { LAUNCHER_SUCCESS, LAUNCHER_WSTR_ERROR };

int file_exists(wchar_t* path) {
    DWORD dwAttrib = GetFileAttributesW(path);
    return (dwAttrib != INVALID_FILE_ATTRIBUTES &&
            !(dwAttrib & FILE_ATTRIBUTE_DIRECTORY));
}

int main(int argc, char** argv) {
    size_t bundle_root_length = strrchr(argv[0], '\\') - argv[0];

    // We don't check the returned value here because there is always at
    // least one '\' in argv[0].

    wchar_t* bundle_root =
        (wchar_t*)calloc(bundle_root_length + 1, sizeof(wchar_t));
    int convert_result =
        MultiByteToWideChar(CP_UTF8, 0, argv[0], (int)bundle_root_length,
                            bundle_root, (int)bundle_root_length);
    if (convert_result <= 0) {
        fprintf(stderr, "Failed to convert the executable path to wstring");
        exit(LAUNCHER_WSTR_ERROR);
    }

    wchar_t* app_main_relative = L"/app/main.py";
    wchar_t* python_home_relative = L"/python";

    wchar_t* app_main = (wchar_t*)calloc(
        bundle_root_length + wcslen(app_main_relative) + 1, sizeof(wchar_t));
    wchar_t* python_home = (wchar_t*)calloc(
        bundle_root_length + wcslen(python_home_relative) + 1, sizeof(wchar_t));

    wcscpy(app_main, bundle_root);
    wcscpy(app_main + bundle_root_length, app_main_relative);

    wcscpy(python_home, bundle_root);
    wcscpy(python_home + bundle_root_length, python_home_relative);

#if PY_MINOR_VERSION >= 11
// Py_SetPythonHome() is deprecated since Python 3.11.
// However being part of the stable ABI it will continue to work.
// See last paragraph of https://peps.python.org/pep-0652/#stable-abi
// The worst case scenario is that it can end up leaking memory,
// but that's not an issue here since it is only used once.
#pragma warning(push)
#pragma warning(disable : 4996)
#endif
    // Tell Python where to find its standard libs.
    // Python computes paths like "HOME/Lib" or "HOME/DLLs" from it.
    Py_SetPythonHome(python_home);
#if PY_MINOR_VERSION >= 11
#pragma warning(pop)
#endif

    // If app/main.py doesn't exist then we don't pass the user's CLI args to
    // the interpreter. In that case it will show its interactive prompt.
    size_t py_argc = file_exists(app_main) ? argc + 2 : 2;
    wchar_t** py_argv = (wchar_t**)calloc(py_argc, sizeof(wchar_t*));
    py_argv[0] = L"-E"; // Ignore PYTHON* environment variables.
    py_argv[1] = L"-s"; // Don't add user site directory to sys.path.

    if (py_argc > 2) {
        py_argv[2] = app_main;
        for (int i = 1; i < argc; i++) {
            int current_py_arg = i + 2;
            size_t arg_length = strlen(argv[i]);
            py_argv[current_py_arg] =
                (wchar_t*)calloc(strlen(argv[i]), sizeof(wchar_t));
            convert_result =
                MultiByteToWideChar(CP_UTF8, 0, argv[i], (int)arg_length,
                                    py_argv[current_py_arg], (int)arg_length);
            if (convert_result <= 0) {
                fprintf(stderr,
                        "Failed to convert this argument to wstring : %s\n",
                        argv[i]);
                exit(LAUNCHER_WSTR_ERROR);
            }
        }
    }

    Py_Initialize();
    Py_Main((int)py_argc, py_argv);

    free(bundle_root);
    free(app_main);
    free(python_home);
    for (size_t i = 3; i < py_argc; ++i) {
        free(py_argv[i]);
    }
    free(py_argv);

    return LAUNCHER_SUCCESS;
}
