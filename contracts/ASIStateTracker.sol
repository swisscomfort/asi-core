// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title ASI State Tracker
 * @dev Smart Contract für anonymes State Tracking im ASI Hybrid Model
 * @notice Speichert nur Zustände (0/1) und CIDs, keine persönlichen Daten
 */
contract ASIStateTracker {
    
    struct StateEntry {
        string key;           // State key (z.B. "walked", "meditated")
        uint256 value;        // State value (0 oder 1)
        string cid;           // IPFS CID für zusätzliche anonyme Daten
        uint256 timestamp;    // Block timestamp
    }
    
    struct GlobalStats {
        uint256 totalEntries;
        uint256 positiveCount;
        uint256 uniqueUsers;
        mapping(address => bool) hasSubmitted;
    }

    struct AggregateData {
        uint256 sum;
        uint256 count;
        uint256 average;
        uint256 lastUpdated;
    }
    
    // Mappings
    mapping(address => StateEntry[]) private userStates;
    mapping(address => mapping(string => uint256)) public userStateValues;
    mapping(address => mapping(string => string)) public userStateCids;
    mapping(string => GlobalStats) private globalStats;
    mapping(string => address[]) private stateUsers;
    mapping(string => uint256) public stateSums;
    mapping(string => uint256) public stateCounts;
    mapping(string => AggregateData) public aggregateStates;
    
    // Events
    event StateLogged(
        address indexed user,
        string key,
        uint256 value,
        string cid,
        uint256 timestamp
    );
    
    event GlobalStatsUpdated(
        string key,
        uint256 totalEntries,
        uint256 positiveCount,
        uint256 uniqueUsers
    );
    
    // Modifiers
    modifier validState(uint256 value) {
        require(value == 0 || value == 1, "State value must be 0 or 1");
        _;
    }
    
    modifier validKey(string memory key) {
        require(bytes(key).length > 0 && bytes(key).length <= 32, "Invalid key length");
        _;
    }
    
    /**
     * @dev Log a state entry for the sender
     * @param key The state key (e.g., "walked", "meditated")
     * @param value The state value (0 or 1)
     * @param cid Optional IPFS CID for additional anonymous data
     */
    function logState(
        string memory key,
        uint256 value,
        string memory cid
    ) external validKey(key) validState(value) {
        
        // Create state entry
        StateEntry memory newEntry = StateEntry({
            key: key,
            value: value,
            cid: cid,
            timestamp: block.timestamp
        });
        
        // Store user state
        userStates[msg.sender].push(newEntry);
        userStateValues[msg.sender][key] = value;
        userStateCids[msg.sender][key] = cid;
        
        // Update aggregation data
        stateSums[key] += value;
        stateCounts[key]++;
        
        // Update aggregate data structure
        AggregateData storage agg = aggregateStates[key];
        agg.sum = stateSums[key];
        agg.count = stateCounts[key];
        agg.average = agg.count > 0 ? (agg.sum * 100) / agg.count : 0; // Percentage
        agg.lastUpdated = block.timestamp;
        
        // Update global stats
        GlobalStats storage stats = globalStats[key];
        
        // Check if user hasn't submitted this state before
        if (!stats.hasSubmitted[msg.sender]) {
            stats.hasSubmitted[msg.sender] = true;
            stats.uniqueUsers++;
            stateUsers[key].push(msg.sender);
        }
        
        stats.totalEntries++;
        if (value == 1) {
            stats.positiveCount++;
        }
        
        // Emit events
        emit StateLogged(msg.sender, key, value, cid, block.timestamp);
        emit GlobalStatsUpdated(key, stats.totalEntries, stats.positiveCount, stats.uniqueUsers);
    }

    /**
     * @dev Get aggregate state data for insights
     * @param key The state key
     * @return sum Total sum of all values
     * @return count Total count of entries
     */
    function getAggregateState(string memory key) public view returns (uint256, uint256) {
        return (stateSums[key], stateCounts[key]);
    }

    /**
     * @dev Get detailed aggregate data
     * @param key The state key
     * @return Aggregate data structure
     */
    function getAggregateData(string memory key) external view returns (AggregateData memory) {
        return aggregateStates[key];
    }

    /**
     * @dev Get multiple aggregate states at once
     * @param keys Array of state keys
     * @return sums Array of sums for each key
     * @return counts Array of counts for each key
     */
    function getMultipleAggregateStates(string[] memory keys) external view returns (
        uint256[] memory sums,
        uint256[] memory counts
    ) {
        sums = new uint256[](keys.length);
        counts = new uint256[](keys.length);
        
        for (uint256 i = 0; i < keys.length; i++) {
            (sums[i], counts[i]) = getAggregateState(keys[i]);
        }
        
        return (sums, counts);
    }
    
    /**
     * @dev Get user's state history for a specific key
     * @param user The user address
     * @param key The state key
     * @return Array of state entries
     */
    function getUserStateHistory(
        address user,
        string memory key
    ) external view returns (StateEntry[] memory) {
        StateEntry[] memory allStates = userStates[user];
        
        // Count matching entries
        uint256 count = 0;
        for (uint256 i = 0; i < allStates.length; i++) {
            if (keccak256(bytes(allStates[i].key)) == keccak256(bytes(key))) {
                count++;
            }
        }
        
        // Create result array
        StateEntry[] memory result = new StateEntry[](count);
        uint256 resultIndex = 0;
        
        for (uint256 i = 0; i < allStates.length; i++) {
            if (keccak256(bytes(allStates[i].key)) == keccak256(bytes(key))) {
                result[resultIndex] = allStates[i];
                resultIndex++;
            }
        }
        
        return result;
    }
    
    /**
     * @dev Get global statistics for a state key
     * @param key The state key
     * @return totalEntries Total number of entries
     * @return positiveCount Number of positive (value=1) entries
     * @return uniqueUsers Number of unique users who submitted this state
     */
    function getGlobalStats(string memory key) external view returns (
        uint256 totalEntries,
        uint256 positiveCount,
        uint256 uniqueUsers
    ) {
        GlobalStats storage stats = globalStats[key];
        return (stats.totalEntries, stats.positiveCount, stats.uniqueUsers);
    }
    
    /**
     * @dev Get user's total number of state entries
     * @param user The user address
     * @return Number of state entries
     */
    function getUserStateCount(address user) external view returns (uint256) {
        return userStates[user].length;
    }
    
    /**
     * @dev Get recent states for a user (last N entries)
     * @param user The user address
     * @param count Number of recent entries to return
     * @return Array of recent state entries
     */
    function getRecentUserStates(
        address user,
        uint256 count
    ) external view returns (StateEntry[] memory) {
        StateEntry[] memory allStates = userStates[user];
        
        if (allStates.length == 0) {
            return new StateEntry[](0);
        }
        
        uint256 returnCount = count > allStates.length ? allStates.length : count;
        StateEntry[] memory result = new StateEntry[](returnCount);
        
        // Return most recent entries
        for (uint256 i = 0; i < returnCount; i++) {
            result[i] = allStates[allStates.length - 1 - i];
        }
        
        return result;
    }
    
    /**
     * @dev Get states by time range
     * @param user The user address
     * @param startTime Start timestamp
     * @param endTime End timestamp
     * @return Array of state entries in time range
     */
    function getStatesByTimeRange(
        address user,
        uint256 startTime,
        uint256 endTime
    ) external view returns (StateEntry[] memory) {
        StateEntry[] memory allStates = userStates[user];
        
        // Count matching entries
        uint256 count = 0;
        for (uint256 i = 0; i < allStates.length; i++) {
            if (allStates[i].timestamp >= startTime && allStates[i].timestamp <= endTime) {
                count++;
            }
        }
        
        // Create result array
        StateEntry[] memory result = new StateEntry[](count);
        uint256 resultIndex = 0;
        
        for (uint256 i = 0; i < allStates.length; i++) {
            if (allStates[i].timestamp >= startTime && allStates[i].timestamp <= endTime) {
                result[resultIndex] = allStates[i];
                resultIndex++;
            }
        }
        
        return result;
    }
    
    /**
     * @dev Check if user has submitted a specific state
     * @param user The user address
     * @param key The state key
     * @return Whether the user has submitted this state
     */
    function hasUserSubmittedState(
        address user,
        string memory key
    ) external view returns (bool) {
        return globalStats[key].hasSubmitted[user];
    }
    
    /**
     * @dev Get positive rate for a state key (for insights)
     * @param key The state key
     * @return Positive rate as percentage (0-100)
     */
    function getPositiveRate(string memory key) external view returns (uint256) {
        GlobalStats storage stats = globalStats[key];
        if (stats.totalEntries == 0) {
            return 0;
        }
        return (stats.positiveCount * 100) / stats.totalEntries;
    }
    
    /**
     * @dev Get all unique state keys (for discovery)
     * Note: This function is gas-intensive and should be used carefully
     * @return Array of all state keys that have been used
     */
    function getAllStateKeys() external view returns (string[] memory) {
        // Note: In a real implementation, you'd maintain a separate array
        // of state keys to make this more efficient
        revert("Function not implemented - use events or off-chain indexing");
    }
    
    /**
     * @dev Emergency function to get contract info
     * @return Contract version and basic stats
     */
    function getContractInfo() external pure returns (
        string memory version,
        string memory description
    ) {
        return (
            "1.0.0",
            "ASI State Tracker - Anonymous state logging for personal development"
        );
    }
}
