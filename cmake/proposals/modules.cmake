# ============================================================================
# ASI-Core Module Proposal - CMake Targets
# ============================================================================
# 
# WICHTIGER HINWEIS: PROPOSAL ONLY - NOT INCLUDED IN BUILD
# 
# Diese Datei dient nur als konzeptioneller Bauplan für eine mögliche
# CMake-basierte Modularisierung. Sie wird NICHT in den Build-Prozess
# eingebunden und verändert keine bestehende Funktionalität.
# 
# Das aktuelle System ist Python-basiert - diese CMake-Definitionen
# dienen als Referenz für zukünftige C++/Qt6-Portierung oder 
# Hybrid-Implementierungen.
# ============================================================================

cmake_minimum_required(VERSION 3.20)

# Modul-Basis-Konfiguration
set(ASI_MODULE_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
set(ASI_INCLUDE_DIR "${ASI_MODULE_DIR}/include")
set(ASI_SOURCE_DIR "${ASI_MODULE_DIR}/src")

# ============================================================================
# Infrastructure Layer - Basis-Module
# ============================================================================

# Common Utilities Module
add_library(asi_common INTERFACE)
target_include_directories(asi_common INTERFACE
    $<BUILD_INTERFACE:${ASI_INCLUDE_DIR}/common>
    $<INSTALL_INTERFACE:include/common>
)
target_sources(asi_common INTERFACE
    # Konzeptionell: config/, requirements.txt Äquivalente
    # Python: gemeinsame Utilities, Logging, Validation
    ${ASI_SOURCE_DIR}/common/logging.cpp
    ${ASI_SOURCE_DIR}/common/config.cpp
    ${ASI_SOURCE_DIR}/common/validation.cpp
    ${ASI_SOURCE_DIR}/common/types.cpp
)
target_compile_features(asi_common INTERFACE cxx_std_20)

# Platform Abstraction Module  
add_library(asi_platform STATIC)
target_include_directories(asi_platform PUBLIC
    $<BUILD_INTERFACE:${ASI_INCLUDE_DIR}/platform>
    $<INSTALL_INTERFACE:include/platform>
)
target_sources(asi_platform PRIVATE
    # Konzeptionell: setup-git.sh, start-pwa.sh Äquivalente
    # Python: plattform-spezifische Implementierungen
    ${ASI_SOURCE_DIR}/platform/filesystem.cpp
    ${ASI_SOURCE_DIR}/platform/process.cpp
    ${ASI_SOURCE_DIR}/platform/environment.cpp
)
target_link_libraries(asi_platform PUBLIC asi_common)

# Test Infrastructure Module
add_library(asi_tests STATIC)
target_include_directories(asi_tests PUBLIC
    $<BUILD_INTERFACE:${ASI_INCLUDE_DIR}/tests>
    $<INSTALL_INTERFACE:include/tests>
)
target_sources(asi_tests PRIVATE
    # Konzeptionell: tests/ Verzeichnis Äquivalente
    # Python: Test-Utilities, Fixtures, Mocks
    ${ASI_SOURCE_DIR}/tests/fixtures.cpp
    ${ASI_SOURCE_DIR}/tests/mocks.cpp
    ${ASI_SOURCE_DIR}/tests/helpers.cpp
)
target_link_libraries(asi_tests PUBLIC 
    asi_common
    # Externe Test-Frameworks
    GTest::gtest
    GTest::gmock
)

# ============================================================================
# Domain Layer - Geschäftslogik
# ============================================================================

# Business Domain Module
add_library(asi_domain STATIC)
target_include_directories(asi_domain PUBLIC
    $<BUILD_INTERFACE:${ASI_INCLUDE_DIR}/domain>
    $<INSTALL_INTERFACE:include/domain>
)
target_sources(asi_domain PRIVATE
    # Konzeptionell: asi_core/state_management.py, src/modules/
    # Python: Fachliche Modelle ohne technische Abhängigkeiten
    ${ASI_SOURCE_DIR}/domain/reflection.cpp
    ${ASI_SOURCE_DIR}/domain/memory.cpp
    ${ASI_SOURCE_DIR}/domain/state.cpp
    ${ASI_SOURCE_DIR}/domain/entities.cpp
)
target_link_libraries(asi_domain PUBLIC asi_common)
# Wichtig: Domain hat KEINE technischen Abhängigkeiten

# ============================================================================
# Service Layer - Fachliche Services
# ============================================================================

# Processing/AI Module
add_library(asi_processing STATIC)
target_include_directories(asi_processing PUBLIC
    $<BUILD_INTERFACE:${ASI_INCLUDE_DIR}/processing>
    $<INSTALL_INTERFACE:include/processing>
)
target_sources(asi_processing PRIVATE
    # Konzeptionell: asi_core/processing.py, asi_core/search.py, src/ai/
    # Python: KI-Integration, Semantic Search, NLP
    ${ASI_SOURCE_DIR}/processing/embedding.cpp
    ${ASI_SOURCE_DIR}/processing/semantic_search.cpp
    ${ASI_SOURCE_DIR}/processing/nlp.cpp
    ${ASI_SOURCE_DIR}/processing/ai_interface.cpp
)
target_link_libraries(asi_processing PUBLIC 
    asi_domain
    asi_common
    asi_platform
    # Externe AI-Libraries
    # TensorFlow::tensorflow_cc
    # OpenAI::openai_cpp
)

# Blockchain Module
add_library(asi_blockchain STATIC)
target_include_directories(asi_blockchain PUBLIC
    $<BUILD_INTERFACE:${ASI_INCLUDE_DIR}/blockchain>
    $<INSTALL_INTERFACE:include/blockchain>
)
target_sources(asi_blockchain PRIVATE
    # Konzeptionell: asi_core/blockchain.py, src/blockchain/, contracts/
    # Python: Web3-Integration, Smart Contracts, Wallet
    ${ASI_SOURCE_DIR}/blockchain/client.cpp
    ${ASI_SOURCE_DIR}/blockchain/contract.cpp
    ${ASI_SOURCE_DIR}/blockchain/wallet.cpp
    ${ASI_SOURCE_DIR}/blockchain/memory_token.cpp
)
target_link_libraries(asi_blockchain PUBLIC
    asi_domain
    asi_common
    asi_platform
    # Externe Blockchain-Libraries
    # Web3::web3cpp
    # OpenSSL::SSL
)

# Storage Module
add_library(asi_storage STATIC)
target_include_directories(asi_storage PUBLIC
    $<BUILD_INTERFACE:${ASI_INCLUDE_DIR}/storage>
    $<INSTALL_INTERFACE:include/storage>
)
target_sources(asi_storage PRIVATE
    # Konzeptionell: asi_core/storage.py, data/, src/storage/
    # Python: SQLite, IPFS, Arweave, Caching
    ${ASI_SOURCE_DIR}/storage/database.cpp
    ${ASI_SOURCE_DIR}/storage/decentralized.cpp
    ${ASI_SOURCE_DIR}/storage/cache.cpp
    ${ASI_SOURCE_DIR}/storage/backup.cpp
)
target_link_libraries(asi_storage PUBLIC
    asi_domain
    asi_common
    asi_platform
    # Externe Storage-Libraries
    # SQLite::sqlite3
    # IPFS::ipfs_client
)

# I/O Module
add_library(asi_io STATIC)
target_include_directories(asi_io PUBLIC
    $<BUILD_INTERFACE:${ASI_INCLUDE_DIR}/io>
    $<INSTALL_INTERFACE:include/io>
)
target_sources(asi_io PRIVATE
    # Konzeptionell: demo_*.py, scripts/
    # Python: Import/Export, Format-Konvertierung
    ${ASI_SOURCE_DIR}/io/import_export.cpp
    ${ASI_SOURCE_DIR}/io/format_converter.cpp
    ${ASI_SOURCE_DIR}/io/file_manager.cpp
    ${ASI_SOURCE_DIR}/io/demo_runner.cpp
)
target_link_libraries(asi_io PUBLIC
    asi_domain
    asi_common
    asi_platform
    # Format-Libraries
    # nlohmann_json::nlohmann_json
    # yaml-cpp::yaml-cpp
)

# Service Layer - Interne Abhängigkeiten (lose gekoppelt)
target_link_libraries(asi_processing PRIVATE asi_storage)  # Cache-Zugriff
target_link_libraries(asi_blockchain PRIVATE asi_storage)  # Persistence
target_link_libraries(asi_io PRIVATE asi_storage)          # Data Access

# ============================================================================
# Application Layer - Orchestrierung
# ============================================================================

# Core Application Module
add_library(asi_core STATIC)
target_include_directories(asi_core PUBLIC
    $<BUILD_INTERFACE:${ASI_INCLUDE_DIR}/core>
    $<INSTALL_INTERFACE:include/core>
)
target_sources(asi_core PRIVATE
    # Konzeptionell: main.py, src/asi_core.py, asi_hybrid_cli.py
    # Python: Hauptorchestrator, CLI, Application Services
    ${ASI_SOURCE_DIR}/core/application.cpp
    ${ASI_SOURCE_DIR}/core/orchestrator.cpp
    ${ASI_SOURCE_DIR}/core/cli.cpp
    ${ASI_SOURCE_DIR}/core/hybrid_model.cpp
)
target_link_libraries(asi_core PUBLIC
    asi_processing
    asi_blockchain
    asi_storage
    asi_io
    asi_domain
    asi_common
    # CLI-Framework
    # CLI11::CLI11
)

# ============================================================================
# UI Layer - Benutzeroberfläche
# ============================================================================

# Web Interface Module (konzeptionell für C++/Qt6)
add_library(asi_web STATIC)
target_include_directories(asi_web PUBLIC
    $<BUILD_INTERFACE:${ASI_INCLUDE_DIR}/web>
    $<INSTALL_INTERFACE:include/web>
)
target_sources(asi_web PRIVATE
    # Konzeptionell: web/, api_server.py, NewReflectionModal_complete.jsx
    # Python → Qt6: Web-Interface, API-Server, PWA-Logik
    ${ASI_SOURCE_DIR}/web/api_server.cpp
    ${ASI_SOURCE_DIR}/web/pwa_manager.cpp
    ${ASI_SOURCE_DIR}/web/ui_components.cpp
    ${ASI_SOURCE_DIR}/web/websocket.cpp
)
target_link_libraries(asi_web PUBLIC
    asi_core
    asi_common
    # UI-Framework
    # Qt6::Core
    # Qt6::Quick
    # Qt6::WebEngine
)

# ============================================================================
# Executable Targets - Hauptprogramme
# ============================================================================

# Haupt-ASI Anwendung
add_executable(asi_app)
target_sources(asi_app PRIVATE
    ${ASI_SOURCE_DIR}/main.cpp  # Äquivalent zu main.py
)
target_link_libraries(asi_app PRIVATE
    asi_core
    asi_web
)

# CLI-Tool
add_executable(asi_cli)
target_sources(asi_cli PRIVATE
    ${ASI_SOURCE_DIR}/cli_main.cpp  # Äquivalent zu asi_hybrid_cli.py
)
target_link_libraries(asi_cli PRIVATE
    asi_core
)

# Demo-Programme
add_executable(asi_demo)
target_sources(asi_demo PRIVATE
    ${ASI_SOURCE_DIR}/demo_main.cpp  # Äquivalent zu demo_*.py
)
target_link_libraries(asi_demo PRIVATE
    asi_io
    asi_core
)

# ============================================================================
# Installation und Export
# ============================================================================

# Installation der Module
install(TARGETS 
    asi_common asi_platform asi_domain
    asi_processing asi_blockchain asi_storage asi_io
    asi_core asi_web asi_tests
    EXPORT asi_targets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)

# Installation der Headers
install(DIRECTORY ${ASI_INCLUDE_DIR}/
    DESTINATION include
    FILES_MATCHING PATTERN "*.hpp"
)

# Export für andere CMake-Projekte
install(EXPORT asi_targets
    FILE asi-config.cmake
    DESTINATION lib/cmake/asi
)

# ============================================================================
# Testing
# ============================================================================

if(BUILD_TESTING)
    enable_testing()
    
    # Unit Tests pro Modul
    add_executable(test_domain)
    target_sources(test_domain PRIVATE tests/unit/test_domain.cpp)
    target_link_libraries(test_domain PRIVATE asi_domain asi_tests)
    add_test(NAME domain_tests COMMAND test_domain)
    
    add_executable(test_processing)
    target_sources(test_processing PRIVATE tests/unit/test_processing.cpp)
    target_link_libraries(test_processing PRIVATE asi_processing asi_tests)
    add_test(NAME processing_tests COMMAND test_processing)
    
    add_executable(test_blockchain)
    target_sources(test_blockchain PRIVATE tests/unit/test_blockchain.cpp)
    target_link_libraries(test_blockchain PRIVATE asi_blockchain asi_tests)
    add_test(NAME blockchain_tests COMMAND test_blockchain)
    
    # Integration Tests
    add_executable(test_integration)
    target_sources(test_integration PRIVATE tests/integration/test_full_system.cpp)
    target_link_libraries(test_integration PRIVATE asi_core asi_tests)
    add_test(NAME integration_tests COMMAND test_integration)
endif()

# ============================================================================
# Packaging
# ============================================================================

set(CPACK_PACKAGE_NAME "asi-core")
set(CPACK_PACKAGE_VERSION "1.0.0")
set(CPACK_PACKAGE_DESCRIPTION "ASI-Core: Artificial Self-Intelligence System")
set(CPACK_PACKAGE_CONTACT "asi-core@example.com")

include(CPack)

# ============================================================================
# Entwickler-Optionen
# ============================================================================

option(ASI_BUILD_DEMOS "Build demo applications" ON)
option(ASI_BUILD_TESTS "Build test suite" ON)
option(ASI_BUILD_DOCS "Build documentation" OFF)
option(ASI_ENABLE_PROFILING "Enable profiling support" OFF)

if(ASI_BUILD_DOCS)
    find_package(Doxygen)
    if(DOXYGEN_FOUND)
        doxygen_add_docs(asi_docs ${ASI_SOURCE_DIR} ${ASI_INCLUDE_DIR})
    endif()
endif()

# ============================================================================
# Compiler-spezifische Einstellungen
# ============================================================================

if(MSVC)
    target_compile_options(asi_common INTERFACE /W4)
else()
    target_compile_options(asi_common INTERFACE -Wall -Wextra -Wpedantic)
endif()

# Debug/Release-spezifische Settings
target_compile_definitions(asi_common INTERFACE
    $<$<CONFIG:Debug>:ASI_DEBUG>
    $<$<CONFIG:Release>:ASI_RELEASE>
)

# ============================================================================
# Abschließende Notizen
# ============================================================================

message(STATUS "ASI-Core Module Proposal configured")
message(STATUS "  - Infrastructure: asi_common, asi_platform, asi_tests")
message(STATUS "  - Domain: asi_domain") 
message(STATUS "  - Services: asi_processing, asi_blockchain, asi_storage, asi_io")
message(STATUS "  - Application: asi_core")
message(STATUS "  - UI: asi_web")
message(STATUS "")
message(STATUS "HINWEIS: Dies ist ein konzeptioneller Bauplan.")
message(STATUS "Aktuelles System basiert auf Python - siehe file-map.json")
message(STATUS "für die Zuordnung der bestehenden Python-Module.")
