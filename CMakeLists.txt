# ASI-Core Build System
cmake_minimum_required(VERSION 3.16)
project(asi-core VERSION 1.0.0 LANGUAGES CXX)

# Build-Optionen
option(ASI_ENABLE_MODULES "Enable modular ASI architecture (INTERFACE targets)" OFF)

# Standard C++ Einstellungen
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include Module-System wenn aktiviert
if(ASI_ENABLE_MODULES)
    message(STATUS "ASI Module System enabled")
    include(cmake/asi-modules.cmake)
else()
    message(STATUS "ASI Module System disabled (default)")
endif()

# Bestehende Build-Logik bleibt unverändert
# (Hier würden normale Targets für das Python-Projekt definiert)
