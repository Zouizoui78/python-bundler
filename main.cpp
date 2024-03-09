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
    //      - existing site directories
    status = PyConfig_SetString(&config, &config.home,
                                python_home.wstring().c_str());
    check_status(status, config);

    // Tell Py_InitializeFromConfig() to not modify config.module_search_paths.
    config.module_search_paths_set = 1;

    // Add standard python libs to sys.path.
    status = PyWideStringList_Append(&config.module_search_paths,
                                     python_zip.wstring().c_str());
    check_status(status, config);

    std::filesystem::path script{argc == 1 ? "app/main.py" : argv[1]};
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