# ASI Module System - INTERFACE Targets
# Dieses File definiert die modulare Architektur als CMake INTERFACE Targets

message(STATUS "Configuring ASI Module System...")

# =============================================================================
# Infrastructure Layer - Basis-Module ohne Business-Logic
# =============================================================================

# common - Utilities, Logging, grundlegende Hilfsfunktionen
add_library(asi_common INTERFACE)
add_library(asi::common ALIAS asi_common)
target_include_directories(asi_common INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/common/include>
    $<INSTALL_INTERFACE:include>
)

# platform - OS-spezifische Implementierungen
add_library(asi_platform INTERFACE)
add_library(asi::platform ALIAS asi_platform)
target_include_directories(asi_platform INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/platform/include>
    $<INSTALL_INTERFACE:include>
)

# tests - Test-Utilities und gemeinsame Test-Infrastruktur
add_library(asi_tests INTERFACE)
add_library(asi::tests ALIAS asi_tests)
target_include_directories(asi_tests INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/tests/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(asi_tests INTERFACE asi_common)

# =============================================================================
# Domain Layer - Geschäftslogik ohne technische Abhängigkeiten
# =============================================================================

# domain - Fachliche Domänen-Logik, Business Rules
add_library(asi_domain INTERFACE)
add_library(asi::domain ALIAS asi_domain)
target_include_directories(asi_domain INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/domain/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(asi_domain INTERFACE asi_common)

# =============================================================================
# Service Layer - Technische Services mit klar definierten APIs
# =============================================================================

# processing - Semantic Search, NLP, Embedding-Generierung
add_library(asi_processing INTERFACE)
add_library(asi::processing ALIAS asi_processing)
target_include_directories(asi_processing INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/processing/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(asi_processing INTERFACE 
    asi_domain 
    asi_common 
    asi_platform
)

# blockchain - Dezentrale Speicherung und Smart Contract-Interaktion  
add_library(asi_blockchain INTERFACE)
add_library(asi::blockchain ALIAS asi_blockchain)
target_include_directories(asi_blockchain INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/blockchain/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(asi_blockchain INTERFACE 
    asi_domain 
    asi_common 
    asi_platform
)

# storage - Lokale und dezentrale Datenpersistierung
add_library(asi_storage INTERFACE)
add_library(asi::storage ALIAS asi_storage)
target_include_directories(asi_storage INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/storage/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(asi_storage INTERFACE 
    asi_domain 
    asi_common 
    asi_platform
)

# io - Ein-/Ausgabe, Import/Export-Funktionalitäten
add_library(asi_io INTERFACE)
add_library(asi::io ALIAS asi_io)
target_include_directories(asi_io INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/io/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(asi_io INTERFACE 
    asi_domain 
    asi_common 
    asi_platform
)

# =============================================================================
# Application Layer - Orchestrierung und Haupteinstiegspunkte
# =============================================================================

# core - Zentrale ASI-Logik und Hauptschnittstellen
add_library(asi_core INTERFACE)
add_library(asi::core ALIAS asi_core)
target_include_directories(asi_core INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/core/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(asi_core INTERFACE 
    asi_processing 
    asi_blockchain 
    asi_storage 
    asi_io 
    asi_domain 
    asi_common
)

# =============================================================================
# UI Layer - Benutzeroberflächen und externe Schnittstellen
# =============================================================================

# web - Frontend PWA und API-Endpunkte
add_library(asi_web INTERFACE)
add_library(asi::web ALIAS asi_web)
target_include_directories(asi_web INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src/web/include>
    $<INSTALL_INTERFACE:include>
)
target_link_libraries(asi_web INTERFACE 
    asi_core 
    asi_common
)

# =============================================================================
# Service Layer - Interne lose Kopplungen (optional)
# =============================================================================

# Optionale Service-zu-Service Abhängigkeiten für erweiterte Funktionalität
# Diese werden als schwache Dependencies modelliert und können zur Laufzeit
# aufgelöst werden, ohne zyklische Abhängigkeiten zu erzeugen

# processing -> storage (für Cache-Funktionalität)
# blockchain -> storage (für Persistierung)  
# io -> storage (für Datenzugriff)
# 
# Diese werden über Dependency Injection oder Service Locator Pattern
# zur Laufzeit aufgelöst, nicht über direkte CMake-Dependencies

# =============================================================================
# Module-Status ausgeben
# =============================================================================

message(STATUS "ASI Module Targets created:")
message(STATUS "  Infrastructure: asi::common, asi::platform, asi::tests")
message(STATUS "  Domain:         asi::domain")
message(STATUS "  Services:       asi::processing, asi::blockchain, asi::storage, asi::io")
message(STATUS "  Application:    asi::core")
message(STATUS "  UI:             asi::web")
message(STATUS "ASI Module System configuration complete!")
