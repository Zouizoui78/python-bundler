cmake_minimum_required(VERSION 3.17)

project(
    python-launcher
    VERSION 0.1
    LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED True)

set(
    SRC
    main.cpp
)

add_executable(${PROJECT_NAME} ${SRC})

find_package(Python3 COMPONENTS Development REQUIRED)
target_link_libraries(${PROJECT_NAME} PRIVATE Python3::Python)