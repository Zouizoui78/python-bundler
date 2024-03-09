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
add_executable(${PROJECT_NAME}-console ${SRC})

find_package(Python3 COMPONENTS Development REQUIRED)
target_link_libraries(${PROJECT_NAME} PRIVATE Python3::Python)
target_link_libraries(${PROJECT_NAME}-console PRIVATE Python3::Python)

# Hide console
target_link_options(${PROJECT_NAME} PRIVATE /SUBSYSTEM:WINDOWS /ENTRY:mainCRTStartup)

add_custom_target(
    dist
    COMMAND python ${CMAKE_SOURCE_DIR}/scripts/release-package.py $<TARGET_FILE:${PROJECT_NAME}> $<TARGET_FILE:${PROJECT_NAME}-console> ${CMAKE_SOURCE_DIR}/scripts/dist.py
)