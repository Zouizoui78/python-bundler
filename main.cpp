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

    auto python_home = std::filesystem::current_path() / "python";
    auto python_zip = python_home / "python312.zip";

    // Set home directory to prevent python from adding its default sys.path.
    // With this sys.path will only contain :
    //      - the working directory from which the executable is launched
    //      - paths manually added with PyWideStringList_Append()
    PyConfig_SetString(&config, &config.home, python_home.wstring().c_str());

    // Tell Py_InitializeFromConfig() to not modify config.module_search_paths.
    config.module_search_paths_set = 1;

    // Add standard python libs to sys.path.
    status = PyWideStringList_Append(&config.module_search_paths,
                                     python_zip.wstring().c_str());
    check_status(status, config);

    std::filesystem::path app_main{"app/main.py"};
    if (argc == 1 && std::filesystem::exists("app/main.py")) {
        // add app directory to sys.path
        status = PyWideStringList_Append(&config.module_search_paths, L"app");
        check_status(status, config);

        // run app/main.py instead of interpreter's main
        status = PyConfig_SetString(&config, &config.run_filename,
                                    app_main.wstring().c_str());
        check_status(status, config);
    }

    status = Py_InitializeFromConfig(&config);
    check_status(status, config);
    PyConfig_Clear(&config);

    return Py_RunMain();
}