cmake_minimum_required(VERSION 3.17)

project(
    python-launcher
    VERSION 0.0.1
    LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED True)

set(
    SRC
    launcher.cpp
)

add_executable(launcher ${SRC})
add_executable(launcher-console ${SRC})

find_package(Python3 COMPONENTS Development REQUIRED)
target_link_libraries(launcher PRIVATE Python3::Python)
target_link_libraries(launcher-console PRIVATE Python3::Python)

# Hide console
target_link_options(launcher PRIVATE /SUBSYSTEM:WINDOWS /ENTRY:mainCRTStartup)

add_custom_target(
    dist
    COMMAND python ${CMAKE_SOURCE_DIR}/cmake/release-package.py $<TARGET_FILE:launcher> $<TARGET_FILE:launcher-console> ${CMAKE_SOURCE_DIR}/bundler.py
)