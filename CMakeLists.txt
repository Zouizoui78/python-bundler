# For the Development.SABIModule components of FindPython
cmake_minimum_required(VERSION 3.26)

project(
    python-launcher
    VERSION 0.2.0
    LANGUAGES CXX
)

# C++17 needed for std::filesystem
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

set(
    SRC
    launcher.cpp
)

add_executable(launcher ${SRC})
add_executable(launcher-console ${SRC})

find_package(Python3 COMPONENTS Development.SABIModule REQUIRED)
target_link_libraries(launcher PRIVATE Python3::SABIModule)
target_link_libraries(launcher-console PRIVATE Python3::SABIModule)

# Hide console
target_link_options(launcher PRIVATE /SUBSYSTEM:WINDOWS /ENTRY:mainCRTStartup)

add_custom_target(
    dist
    COMMAND python ${CMAKE_SOURCE_DIR}/cmake/release-package.py $<TARGET_FILE:launcher> $<TARGET_FILE:launcher-console> ${CMAKE_SOURCE_DIR}/bundler.py
)
