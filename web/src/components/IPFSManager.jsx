import { useState, useEffect } from 'react';

export default function IPFSManager({ className = "" }) {
  const [isConnected, setIsConnected] = useState(false);
  const [nodeInfo, setNodeInfo] = useState(null);
  const [pinnedFiles, setPinnedFiles] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(null);

  const IPFS_API = 'http://127.0.0.1:5001';
  const IPFS_GATEWAY = 'http://127.0.0.1:8080';

  useEffect(() => {
    checkIPFSConnection();
  }, []);

  const checkIPFSConnection = async () => {
    try {
      const response = await fetch(`${IPFS_API}/api/v0/version`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const info = await response.json();
        setNodeInfo(info);
        setIsConnected(true);
        loadPinnedFiles();
      } else {
        setIsConnected(false);
      }
    } catch (error) {
      setIsConnected(false);
      setNodeInfo(null);
    }
  };

  const loadPinnedFiles = async () => {
    try {
      const response = await fetch(`${IPFS_API}/api/v0/pin/ls`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const data = await response.json();
        const pins = Object.entries(data.Keys || {}).map(([hash, info]) => ({
          hash,
          type: info.Type,
          size: 'Unknown'
        }));
        setPinnedFiles(pins.slice(0, 10)); // Show latest 10
      }
    } catch (error) {
      console.error('Failed to load pinned files:', error);
    }
  };

  const uploadFile = async (file) => {
    if (!isConnected) {
      alert('IPFS node not connected');
      return null;
    }

    setIsLoading(true);
    setUploadProgress({ name: file.name, progress: 0 });

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${IPFS_API}/api/v0/add?pin=true`, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        setUploadProgress({ name: file.name, progress: 100 });
        
        setTimeout(() => {
          setUploadProgress(null);
          loadPinnedFiles();
        }, 1000);

        return result.Hash;
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload file to IPFS');
      return null;
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      const hash = await uploadFile(file);
      if (hash) {
        alert(`File uploaded successfully!\nIPFS Hash: ${hash}`);
      }
    }
  };

  const handleDrop = async (event) => {
    event.preventDefault();
    const files = Array.from(event.dataTransfer.files);
    
    for (const file of files) {
      await uploadFile(file);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  const openInGateway = (hash) => {
    window.open(`${IPFS_GATEWAY}/ipfs/${hash}`, '_blank');
  };

  return (
    <div className={`bg-white border border-gray-200 rounded-lg ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900">IPFS Storage</h2>
            <p className="text-gray-600 text-sm">
              Decentralized file storage for ASI Core
            </p>
          </div>
          
          {/* Connection Status */}
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
            <span className={`text-sm font-medium ${isConnected ? 'text-green-700' : 'text-red-700'}`}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
            <button
              onClick={checkIPFSConnection}
              className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm"
            >
              ↻
            </button>
          </div>
        </div>

        {/* Node Info */}
        {nodeInfo && (
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
            <div className="text-sm">
              <strong>IPFS Version:</strong> {nodeInfo.Version} | 
              <strong> Commit:</strong> {nodeInfo.Commit?.slice(0, 8)}
            </div>
          </div>
        )}
      </div>

      {isConnected ? (
        <>
          {/* Upload Area */}
          <div className="p-6 border-b border-gray-200">
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors"
            >
              <div className="mb-4">
                <div className="w-16 h-16 mx-auto bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-2xl">📁</span>
                </div>
              </div>
              
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Upload to IPFS
              </h3>
              
              <p className="text-gray-600 mb-4 text-sm">
                Drag and drop files here, or click to select
              </p>
              
              <input
                type="file"
                onChange={handleFileUpload}
                className="hidden"
                id="file-upload"
                multiple
              />
              
              <label
                htmlFor="file-upload"
                className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium cursor-pointer hover:bg-blue-700 transition-colors inline-block"
              >
                Select Files
              </label>
            </div>

            {/* Upload Progress */}
            {uploadProgress && (
              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Uploading: {uploadProgress.name}</span>
                  <span className="text-sm text-blue-600">{uploadProgress.progress}%</span>
                </div>
                <div className="w-full bg-blue-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${uploadProgress.progress}%` }}
                  ></div>
                </div>
              </div>
            )}
          </div>

          {/* Pinned Files */}
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">
                Pinned Files ({pinnedFiles.length})
              </h3>
              <button
                onClick={loadPinnedFiles}
                disabled={isLoading}
                className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm"
              >
                {isLoading ? '🔄' : '↻'} Refresh
              </button>
            </div>

            {pinnedFiles.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <div className="text-4xl mb-2">📌</div>
                <div>No files pinned yet</div>
              </div>
            ) : (
              <div className="space-y-3">
                {pinnedFiles.map((file, index) => (
                  <div
                    key={file.hash}
                    className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="font-mono text-sm text-gray-900 truncate">
                        {file.hash}
                      </div>
                      <div className="text-xs text-gray-500">
                        Type: {file.type} | Size: {file.size}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2 ml-4">
                      <button
                        onClick={() => copyToClipboard(file.hash)}
                        className="px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded text-xs"
                        title="Copy hash"
                      >
                        📋
                      </button>
                      <button
                        onClick={() => openInGateway(file.hash)}
                        className="px-2 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded text-xs"
                        title="Open in gateway"
                      >
                        🔗
                      </button>
                    </div>
                  </div>
                ))}
                
                {pinnedFiles.length >= 10 && (
                  <div className="text-center text-sm text-gray-500 pt-2">
                    Showing latest 10 files. Use IPFS CLI for full list.
                  </div>
                )}
              </div>
            )}
          </div>
        </>
      ) : (
        /* Not Connected */
        <div className="p-8 text-center">
          <div className="w-16 h-16 mx-auto bg-red-100 rounded-full flex items-center justify-center mb-4">
            <span className="text-2xl">⚠️</span>
          </div>
          
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            IPFS Node Not Available
          </h3>
          
          <p className="text-gray-600 mb-6 text-sm max-w-md mx-auto">
            To use decentralized storage, you need to install and run an IPFS node locally.
          </p>
          
          <div className="space-y-4 max-w-lg mx-auto text-left">
            <div className="bg-gray-50 border border-gray-200 rounded p-4">
              <h4 className="font-medium text-gray-900 mb-2">Installation Steps:</h4>
              <ol className="text-sm text-gray-600 space-y-1">
                <li>1. Install IPFS: <code className="bg-gray-200 px-1 rounded">curl -sSL https://dist.ipfs.tech/kubo/v0.22.0/kubo_v0.22.0_linux-amd64.tar.gz | tar -xz</code></li>
                <li>2. Initialize: <code className="bg-gray-200 px-1 rounded">ipfs init</code></li>
                <li>3. Start daemon: <code className="bg-gray-200 px-1 rounded">ipfs daemon</code></li>
                <li>4. Refresh this page</li>
              </ol>
            </div>
          </div>
          
          <button
            onClick={checkIPFSConnection}
            className="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Check Connection Again
          </button>
        </div>
      )}
    </div>
  );
}