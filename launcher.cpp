#include <Python.h>
#include <filesystem>

void check_status(PyStatus& status, PyConfig& config) {
    if (PyStatus_Exception(status)) {
        PyConfig_Clear(&config);
        if (PyStatus_IsExit(status)) {
            exit(status.exitcode);
        }
        Py_ExitStatusException(status);
    }
}

int main(int argc, char** argv) {
    PyStatus status;
    PyConfig config;

    // Run python in isolated mode, i.e. :
    //      - don't add "unsafe" paths to sys.path
    //      - ignore env vars
    //      - ignore user site directory
    PyConfig_InitIsolatedConfig(&config);

    auto bundle_root = std::filesystem::path(argv[0]).parent_path();
    auto app_main = bundle_root / "app" / "main.py";
    auto python_home = bundle_root / "python";
    auto python_lib = python_home / "Lib";

    // Set home directory to prevent python from adding its default sys.path.
    // With this sys.path will only contain :
    //      - paths manually added with PyWideStringList_Append()
    //      - existing site-packages directories, in our case :
    //          - the python directory
    //          - <python directory>/Lib/site-packages
    status = PyConfig_SetString(&config, &config.home,
                                python_home.wstring().c_str());
    check_status(status, config);

    // Tell Py_InitializeFromConfig() to not modify config.module_search_paths.
    config.module_search_paths_set = 1;

    // Add standard python libs to sys.path.
    status = PyWideStringList_Append(&config.module_search_paths,
                                     python_lib.wstring().c_str());
    check_status(status, config);

    std::filesystem::path script{argc == 1 ? app_main : argv[1]};
    if (std::filesystem::exists(script)) {
        // Add app directory to sys.path.
        status =
            PyWideStringList_Append(&config.module_search_paths,
                                    script.parent_path().wstring().c_str());
        check_status(status, config);

        // Run target script instead of interpreter's main.
        status = PyConfig_SetString(&config, &config.run_filename,
                                    script.wstring().c_str());
        check_status(status, config);
    }

    status = Py_InitializeFromConfig(&config);
    check_status(status, config);
    PyConfig_Clear(&config);

    // Run config.run_filename if it's set.
    // If not, run the interpreter.
    return Py_RunMain();
}