cmake_minimum_required(VERSION 3.16)
project(BafyamConverter VERSION 3.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

# Buscar Qt6
find_package(Qt6 REQUIRED COMPONENTS Core Gui Widgets)

set(APP_SOURCES
    src/main.cpp
    src/MainWindow.cpp
    src/MainWindow.h
    resources.qrc
    resources/app.rc
)

add_executable(BafyamConverter ${APP_SOURCES})

# Enlazar Qt
target_link_libraries(BafyamConverter PRIVATE Qt6::Core Qt6::Gui Qt6::Widgets)

# Ocultar la consola negra de Windows y compilar como app con ventana
set_target_properties(BafyamConverter PROPERTIES
    WIN32_EXECUTABLE TRUE
)
