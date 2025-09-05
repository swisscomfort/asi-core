// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title ASIIndex
 * @dev Smart Contract für die Indexierung von ASI (Autonomous Self-Improvement) Einträgen
 * Speichert Metadaten von Reflexionen und ermöglicht dezentrale Indexierung
 */
contract ASIIndex is Ownable, ReentrancyGuard {
    
    // Struktur für einen ASI-Eintrag
    struct Entry {
        uint256 entryId;        // Eindeutige ID des Eintrags
        string cid;             // IPFS/Arweave Content Identifier
        string[] tags;          // Tags für Kategorisierung
        bytes embedding;        // AI-Embedding für semantische Suche
        uint8 stateValue;       // Binärer/numerischer Zustandswert (0, 1, oder andere kleine Werte)
        uint256 timestamp;      // Zeitstempel der Erstellung
        address owner;          // Adresse des Erstellers
        bool isActive;          // Status des Eintrags
    }
    
    // Mapping: entryId => Entry
    mapping(uint256 => Entry) public entries;
    
    // Mapping: owner => entryIds[]
    mapping(address => uint256[]) public ownerEntries;
    
    // Mapping: tag => entryIds[]
    mapping(string => uint256[]) public tagEntries;
    
    // Zähler für eindeutige Entry IDs
    uint256 private nextEntryId = 1;
    
    // Maximale Anzahl Tags pro Eintrag
    uint256 public constant MAX_TAGS = 10;
    
    // Maximale Größe des Embeddings (in Bytes)
    uint256 public constant MAX_EMBEDDING_SIZE = 1024;
    
    // Events
    event EntryRegistered(
        uint256 indexed entryId,
        string indexed cid,
        address indexed owner,
        uint8 stateValue,
        uint256 timestamp
    );
    
    event EntryUpdated(
        uint256 indexed entryId,
        string indexed cid,
        uint256 timestamp
    );
    
    event EntryDeactivated(
        uint256 indexed entryId,
        uint256 timestamp
    );
    
    event TagAdded(
        uint256 indexed entryId,
        string indexed tag
    );
    
    constructor() Ownable(msg.sender) {}
    
    /**
     * @dev Registriert einen neuen ASI-Eintrag mit Zustandswert (Hybrid-Modell)
     * @param _cid Content Identifier (IPFS/Arweave)
     * @param _tags Array von Tags für Kategorisierung
     * @param _embedding AI-Embedding als Bytes
     * @param _stateValue Zustandswert (0, 1, oder andere kleine numerische Werte)
     * @param _timestamp Zeitstempel der Erstellung
     * @return entryId Die ID des erstellten Eintrags
     */
    function registerHybridEntry(
        string memory _cid,
        string[] memory _tags,
        bytes memory _embedding,
        uint8 _stateValue,
        uint256 _timestamp
    ) external nonReentrant returns (uint256) {
        // Validierungen
        require(bytes(_cid).length > 0, "CID darf nicht leer sein");
        require(_tags.length <= MAX_TAGS, "Zu viele Tags");
        require(_embedding.length <= MAX_EMBEDDING_SIZE, "Embedding zu gross");
        require(_timestamp > 0, "Timestamp muss gesetzt sein");
        
        uint256 entryId = nextEntryId++;
        
        // Entry erstellen
        Entry storage newEntry = entries[entryId];
        newEntry.entryId = entryId;
        newEntry.cid = _cid;
        newEntry.tags = _tags;
        newEntry.embedding = _embedding;
        newEntry.stateValue = _stateValue;
        newEntry.timestamp = _timestamp;
        newEntry.owner = msg.sender;
        newEntry.isActive = true;
        
        // Owner-Mapping aktualisieren
        ownerEntries[msg.sender].push(entryId);
        
        // Tag-Mappings aktualisieren
        for (uint256 i = 0; i < _tags.length; i++) {
            if (bytes(_tags[i]).length > 0) {
                tagEntries[_tags[i]].push(entryId);
                emit TagAdded(entryId, _tags[i]);
            }
        }
        
        emit EntryRegistered(entryId, _cid, msg.sender, _stateValue, _timestamp);
        
        return entryId;
    }
    
    /**
     * @dev Registriert einen neuen ASI-Eintrag (Legacy-Funktion für Rückwärtskompatibilität)
     * @param _cid Content Identifier (IPFS/Arweave)
     * @param _tags Array von Tags für Kategorisierung
     * @param _embedding AI-Embedding als Bytes
     * @param _timestamp Zeitstempel der Erstellung
     * @return entryId Die ID des erstellten Eintrags
     */
    function registerEntry(
        string memory _cid,
        string[] memory _tags,
        bytes memory _embedding,
        uint256 _timestamp
    ) external nonReentrant returns (uint256) {
        // Validierungen
        require(bytes(_cid).length > 0, "CID darf nicht leer sein");
        require(_tags.length <= MAX_TAGS, "Zu viele Tags");
        require(_embedding.length <= MAX_EMBEDDING_SIZE, "Embedding zu gross");
        require(_timestamp > 0, "Timestamp muss gesetzt sein");
        
        uint256 entryId = nextEntryId++;
        
        // Entry erstellen mit Standardzustand 0
        Entry storage newEntry = entries[entryId];
        newEntry.entryId = entryId;
        newEntry.cid = _cid;
        newEntry.tags = _tags;
        newEntry.embedding = _embedding;
        newEntry.stateValue = 0; // Standardzustand für Legacy-Einträge
        newEntry.timestamp = _timestamp;
        newEntry.owner = msg.sender;
        newEntry.isActive = true;
        
        // Owner-Mapping aktualisieren
        ownerEntries[msg.sender].push(entryId);
        
        // Tag-Mappings aktualisieren
        for (uint256 i = 0; i < _tags.length; i++) {
            if (bytes(_tags[i]).length > 0) {
                tagEntries[_tags[i]].push(entryId);
                emit TagAdded(entryId, _tags[i]);
            }
        }
        
        emit EntryRegistered(entryId, _cid, msg.sender, 0, _timestamp);
        
        return entryId;
    }
    
    /**
     * @dev Aktualisiert einen bestehenden Eintrag (nur Owner)
     * @param _entryId ID des zu aktualisierenden Eintrags
     * @param _cid Neuer Content Identifier
     * @param _embedding Neues AI-Embedding
     */
    function updateEntry(
        uint256 _entryId,
        string memory _cid,
        bytes memory _embedding
    ) external nonReentrant {
        require(_entryId < nextEntryId, "Eintrag existiert nicht");
        require(entries[_entryId].owner == msg.sender, "Nur Owner kann aktualisieren");
        require(entries[_entryId].isActive, "Eintrag ist deaktiviert");
        require(bytes(_cid).length > 0, "CID darf nicht leer sein");
        require(_embedding.length <= MAX_EMBEDDING_SIZE, "Embedding zu gross");
        
        entries[_entryId].cid = _cid;
        entries[_entryId].embedding = _embedding;
        
        emit EntryUpdated(_entryId, _cid, block.timestamp);
    }
    
    /**
     * @dev Deaktiviert einen Eintrag (nur Owner)
     * @param _entryId ID des zu deaktivierenden Eintrags
     */
    function deactivateEntry(uint256 _entryId) external nonReentrant {
        require(_entryId < nextEntryId, "Eintrag existiert nicht");
        require(entries[_entryId].owner == msg.sender, "Nur Owner kann deaktivieren");
        require(entries[_entryId].isActive, "Eintrag bereits deaktiviert");
        
        entries[_entryId].isActive = false;
        
        emit EntryDeactivated(_entryId, block.timestamp);
    }
    
    /**
     * @dev Gibt alle Einträge eines Owners zurück
     * @param _owner Adresse des Owners
     * @return Array von Entry IDs
     */
    function getEntriesByOwner(address _owner) external view returns (uint256[] memory) {
        return ownerEntries[_owner];
    }
    
    /**
     * @dev Gibt alle Einträge mit einem bestimmten Tag zurück
     * @param _tag Der zu suchende Tag
     * @return Array von Entry IDs
     */
    function getEntriesByTag(string memory _tag) external view returns (uint256[] memory) {
        return tagEntries[_tag];
    }
    
    /**
     * @dev Gibt Details eines Eintrags zurück
     * @param _entryId ID des Eintrags
     * @return Entry-Struktur
     */
    function getEntry(uint256 _entryId) external view returns (Entry memory) {
        require(_entryId < nextEntryId, "Eintrag existiert nicht");
        return entries[_entryId];
    }
    
    /**
     * @dev Gibt die Anzahl der registrierten Einträge zurück
     * @return Anzahl der Einträge
     */
    function getTotalEntries() external view returns (uint256) {
        return nextEntryId - 1;
    }
    
    /**
     * @dev Überprüft ob ein Eintrag existiert und aktiv ist
     * @param _entryId ID des Eintrags
     * @return true wenn aktiv, false sonst
     */
    function isEntryActive(uint256 _entryId) external view returns (bool) {
        return _entryId < nextEntryId && entries[_entryId].isActive;
    }
    
    /**
     * @dev Gibt das Embedding eines Eintrags zurück (nur für semantische Suche)
     * @param _entryId ID des Eintrags
     * @return Das Embedding als Bytes
     */
    function getEntryEmbedding(uint256 _entryId) external view returns (bytes memory) {
        require(_entryId < nextEntryId, "Eintrag existiert nicht");
        require(entries[_entryId].isActive, "Eintrag ist deaktiviert");
        return entries[_entryId].embedding;
    }
    
    /**
     * @dev Batch-Funktion um mehrere Einträge auf einmal zu holen
     * @param _entryIds Array von Entry IDs
     * @return Array von Entry-Strukturen
     */
    function getBatchEntries(uint256[] memory _entryIds) external view returns (Entry[] memory) {
        Entry[] memory result = new Entry[](_entryIds.length);
        
        for (uint256 i = 0; i < _entryIds.length; i++) {
            require(_entryIds[i] < nextEntryId, "Ein oder mehrere Eintraege existieren nicht");
            result[i] = entries[_entryIds[i]];
        }
        
        return result;
    }
    
    /**
     * @dev Gibt alle Einträge mit einem bestimmten Zustandswert zurück
     * @param _stateValue Der zu suchende Zustandswert
     * @return Array von Entry IDs
     */
    function getEntriesByState(uint8 _stateValue) external view returns (uint256[] memory) {
        uint256[] memory tempResult = new uint256[](nextEntryId - 1);
        uint256 count = 0;
        
        // Durch alle Einträge iterieren und nach Zustand filtern
        for (uint256 i = 1; i < nextEntryId; i++) {
            if (entries[i].isActive && entries[i].stateValue == _stateValue) {
                tempResult[count] = i;
                count++;
            }
        }
        
        // Ergebnisarray auf richtige Größe trimmen
        uint256[] memory result = new uint256[](count);
        for (uint256 i = 0; i < count; i++) {
            result[i] = tempResult[i];
        }
        
        return result;
    }
    
    /**
     * @dev Gibt Statistiken über Zustandsverteilung zurück
     * @return states Array mit verschiedenen Zuständen
     * @return counts Array mit der Anzahl pro Zustand
     */
    function getStateStatistics() external view returns (uint8[] memory states, uint256[] memory counts) {
        // Maximale Anzahl verschiedener Zustände (0-255 für uint8)
        uint256[] memory stateCounts = new uint256[](256);
        uint256 uniqueStates = 0;
        
        // Zustände zählen
        for (uint256 i = 1; i < nextEntryId; i++) {
            if (entries[i].isActive) {
                uint8 state = entries[i].stateValue;
                if (stateCounts[state] == 0) {
                    uniqueStates++;
                }
                stateCounts[state]++;
            }
        }
        
        // Ergebnisarrays erstellen
        states = new uint8[](uniqueStates);
        counts = new uint256[](uniqueStates);
        
        uint256 index = 0;
        for (uint256 i = 0; i < 256; i++) {
            if (stateCounts[i] > 0) {
                states[index] = uint8(i);
                counts[index] = stateCounts[i];
                index++;
            }
        }
        
        return (states, counts);
    }
}
