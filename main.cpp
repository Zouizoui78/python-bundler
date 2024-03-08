#include <Python.h>
#include <filesystem>
#include <iostream>

int main(int argc, char** argv) {
    PyStatus status;

    PyConfig config;
    PyConfig_InitPythonConfig(&config);

    if (argc == 1 && std::filesystem::exists("main.py")) {
        PyConfig_SetString(&config, &config.run_filename, L"main.py");
    }

    status = PyConfig_SetBytesArgv(&config, argc, argv);
    if (PyStatus_Exception(status)) {
        goto exception;
    }

    status = Py_InitializeFromConfig(&config);
    if (PyStatus_Exception(status)) {
        goto exception;
    }
    PyConfig_Clear(&config);

    return Py_RunMain();

exception:
    PyConfig_Clear(&config);
    if (PyStatus_IsExit(status)) {
        return status.exitcode;
    }
    Py_ExitStatusException(status);
}