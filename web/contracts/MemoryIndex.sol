// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";

contract MemoryIndex is Ownable {
    struct Memory {
        string cid;
        string[] tags;
        int256[768] embedding;
        uint256 timestamp;
        address owner;
        bool shared;
    }
    
    Memory[] public memories;
    mapping(address => uint256[]) public userMemoryIndices;
    mapping(string => bool) public cidExists;
    
    event MemoryStored(address indexed owner, string cid, string[] tags);
    
    constructor() Ownable(msg.sender) {}
    
    function addMemory(
        string memory _cid,
        string[] memory _tags,
        int256[768] memory _embedding
    ) external {
        require(!cidExists[_cid], "CID already exists");
        
        Memory memory newMemory = Memory({
            cid: _cid,
            tags: _tags,
            embedding: _embedding,
            timestamp: block.timestamp,
            owner: msg.sender,
            shared: true
        });
        
        uint256 index = memories.length;
        memories.push(newMemory);
        userMemoryIndices[msg.sender].push(index);
        cidExists[_cid] = true;
        
        emit MemoryStored(msg.sender, _cid, _tags);
    }
    
    function getMemory(uint256 index) external view returns (
        string memory cid,
        string[] memory tags,
        int256[768] memory embedding,
        uint256 timestamp,
        address owner,
        bool shared
    ) {
        require(index < memories.length, "Invalid index");
        Memory memory mem = memories[index];
        return (mem.cid, mem.tags, mem.embedding, mem.timestamp, mem.owner, mem.shared);
    }
    
    function getTotalMemories() external view returns (uint256) {
        return memories.length;
    }
    
    function getUserMemoryCount(address user) external view returns (uint256) {
        return userMemoryIndices[user].length;
    }
    
    function getUserMemoryIndex(address user, uint256 userIndex) external view returns (uint256) {
        require(userIndex < userMemoryIndices[user].length, "Invalid user index");
        return userMemoryIndices[user][userIndex];
    }
}
