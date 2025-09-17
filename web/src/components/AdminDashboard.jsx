import React, { useState, useEffect } from "react";
import {
  Cog6ToothIcon,
  ChartBarIcon,
  UserGroupIcon,
  DatabaseIcon,
  ShieldCheckIcon,
  BellIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  DocumentArrowDownIcon,
  TrashIcon,
  EyeIcon,
  ServerIcon,
  CpuChipIcon,
  CloudIcon,
} from "@heroicons/react/24/outline";

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState("overview");
  const [systemStats, setSystemStats] = useState({});
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [alerts, setAlerts] = useState([]);
  const [services, setServices] = useState({});

  useEffect(() => {
    loadAdminData();
    const interval = setInterval(loadAdminData, 30000); // Update alle 30 Sekunden
    return () => clearInterval(interval);
  }, []);

  const loadAdminData = async () => {
    setLoading(true);
    try {
      // System Stats laden
      const statsResponse = await fetch("/api/admin/stats");
      if (statsResponse.ok) {
        const stats = await statsResponse.json();
        setSystemStats(stats);
      }

      // Services Status laden
      const servicesResponse = await fetch("/api/admin/services");
      if (servicesResponse.ok) {
        const servicesData = await servicesResponse.json();
        setServices(servicesData);
      }

      // Alerts laden
      const alertsResponse = await fetch("/api/admin/alerts");
      if (alertsResponse.ok) {
        const alertsData = await alertsResponse.json();
        setAlerts(alertsData);
      }

      // Recent Logs laden
      const logsResponse = await fetch("/api/admin/logs?limit=50");
      if (logsResponse.ok) {
        const logsData = await logsResponse.json();
        setLogs(logsData);
      }
    } catch (error) {
      console.error("Failed to load admin data:", error);
    } finally {
      setLoading(false);
    }
  };

  const restartService = async (serviceName) => {
    try {
      const response = await fetch(`/api/admin/services/${serviceName}/restart`, {
        method: "POST",
      });
      if (response.ok) {
        loadAdminData(); // Refresh data
        alert(`Service ${serviceName} wurde neu gestartet`);
      }
    } catch (error) {
      alert(`Fehler beim Neustarten von ${serviceName}: ${error.message}`);
    }
  };

  const exportData = async (dataType) => {
    try {
      const response = await fetch(`/api/admin/export/${dataType}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `asi-core-${dataType}-${new Date().toISOString().split("T")[0]}.json`;
        a.click();
      }
    } catch (error) {
      alert(`Export-Fehler: ${error.message}`);
    }
  };

  const clearLogs = async () => {
    if (confirm("Sind Sie sicher, dass Sie alle Logs löschen möchten?")) {
      try {
        const response = await fetch("/api/admin/logs", { method: "DELETE" });
        if (response.ok) {
          setLogs([]);
          alert("Logs wurden gelöscht");
        }
      } catch (error) {
        alert(`Fehler beim Löschen der Logs: ${error.message}`);
      }
    }
  };

  const AdminTabs = () => (
    <div className="border-b border-gray-200 mb-6">
      <nav className="-mb-px flex space-x-8">
        {[
          { id: "overview", name: "Übersicht", icon: ChartBarIcon },
          { id: "services", name: "Services", icon: ServerIcon },
          { id: "database", name: "Datenbank", icon: DatabaseIcon },
          { id: "agents", name: "Agenten", icon: UserGroupIcon },
          { id: "blockchain", name: "Blockchain", icon: CpuChipIcon },
          { id: "storage", name: "Storage", icon: CloudIcon },
          { id: "logs", name: "Logs", icon: DocumentArrowDownIcon },
          { id: "settings", name: "Einstellungen", icon: Cog6ToothIcon },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`${
              activeTab === tab.id
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center gap-2`}
          >
            <tab.icon className="h-4 w-4" />
            {tab.name}
          </button>
        ))}
      </nav>
    </div>
  );

  const OverviewTab = () => (
    <div className="space-y-6">
      {/* System Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow border-l-4 border-green-500">
          <div className="flex items-center">
            <CheckCircleIcon className="h-8 w-8 text-green-500" />
            <div className="ml-4">
              <h3 className="text-lg font-semibold">System Status</h3>
              <p className="text-green-600">Online</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <UserGroupIcon className="h-8 w-8 text-blue-500" />
            <div className="ml-4">
              <h3 className="text-lg font-semibold">Aktive Agenten</h3>
              <p className="text-2xl font-bold">{systemStats.active_agents || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <DatabaseIcon className="h-8 w-8 text-purple-500" />
            <div className="ml-4">
              <h3 className="text-lg font-semibold">Reflexionen</h3>
              <p className="text-2xl font-bold">{systemStats.total_reflections || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <CpuChipIcon className="h-8 w-8 text-orange-500" />
            <div className="ml-4">
              <h3 className="text-lg font-semibold">CPU Load</h3>
              <p className="text-2xl font-bold">{systemStats.cpu_usage || 0}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <BellIcon className="h-5 w-5" />
              System Alerts
            </h3>
          </div>
          <div className="p-6">
            {alerts.map((alert, index) => (
              <div
                key={index}
                className={`flex items-center p-3 rounded mb-2 ${
                  alert.level === "error"
                    ? "bg-red-50 text-red-700"
                    : alert.level === "warning"
                    ? "bg-yellow-50 text-yellow-700"
                    : "bg-blue-50 text-blue-700"
                }`}
              >
                {alert.level === "error" ? (
                  <XCircleIcon className="h-5 w-5 mr-2" />
                ) : (
                  <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
                )}
                {alert.message}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h3 className="text-lg font-semibold">Quick Actions</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => exportData("full")}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              <DocumentArrowDownIcon className="h-4 w-4" />
              Vollexport
            </button>
            <button
              onClick={() => loadAdminData()}
              className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              <ArrowPathIcon className="h-4 w-4" />
              Aktualisieren
            </button>
            <button
              onClick={clearLogs}
              className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
            >
              <TrashIcon className="h-4 w-4" />
              Logs löschen
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  const ServicesTab = () => (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b">
        <h3 className="text-lg font-semibold">System Services</h3>
      </div>
      <div className="p-6">
        <div className="space-y-4">
          {Object.entries(services).map(([serviceName, serviceData]) => (
            <div key={serviceName} className="flex items-center justify-between p-4 border rounded">
              <div className="flex items-center gap-3">
                <div
                  className={`h-3 w-3 rounded-full ${
                    serviceData.status === "running" ? "bg-green-500" : "bg-red-500"
                  }`}
                />
                <div>
                  <h4 className="font-semibold">{serviceName}</h4>
                  <p className="text-sm text-gray-600">{serviceData.description}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span
                  className={`px-2 py-1 rounded text-xs ${
                    serviceData.status === "running"
                      ? "bg-green-100 text-green-800"
                      : "bg-red-100 text-red-800"
                  }`}
                >
                  {serviceData.status}
                </span>
                <button
                  onClick={() => restartService(serviceName)}
                  className="px-3 py-1 bg-blue-500 text-white rounded text-xs hover:bg-blue-600"
                >
                  Restart
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const LogsTab = () => (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b flex justify-between items-center">
        <h3 className="text-lg font-semibold">System Logs</h3>
        <button
          onClick={clearLogs}
          className="px-3 py-1 bg-red-500 text-white rounded text-sm hover:bg-red-600"
        >
          Logs löschen
        </button>
      </div>
      <div className="p-6">
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {logs.map((log, index) => (
            <div key={index} className="text-sm font-mono p-2 bg-gray-50 rounded">
              <span className="text-gray-500">{log.timestamp}</span>{" "}
              <span className={`font-semibold ${
                log.level === "ERROR" ? "text-red-600" : 
                log.level === "WARNING" ? "text-yellow-600" : "text-gray-700"
              }`}>
                [{log.level}]
              </span>{" "}
              {log.message}
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <ArrowPathIcon className="h-8 w-8 animate-spin text-blue-500" />
        <span className="ml-2">Lade Admin-Dashboard...</span>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <ShieldCheckIcon className="h-8 w-8 text-blue-500" />
          ASI-Core Admin Dashboard
        </h1>
        <p className="text-gray-600 mt-2">
          Zentrale Verwaltung und Überwachung des ASI-Core Systems
        </p>
      </div>

      <AdminTabs />

      {activeTab === "overview" && <OverviewTab />}
      {activeTab === "services" && <ServicesTab />}
      {activeTab === "logs" && <LogsTab />}
      {activeTab === "database" && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Datenbank Management</h3>
          <p>Datenbank-Tools werden hier implementiert...</p>
        </div>
      )}
      {activeTab === "agents" && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Agent Management</h3>
          <p>Agent-Verwaltung wird hier implementiert...</p>
        </div>
      )}
      {activeTab === "blockchain" && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Blockchain Monitoring</h3>
          <p>Blockchain-Überwachung wird hier implementiert...</p>
        </div>
      )}
      {activeTab === "storage" && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Storage Management</h3>
          <p>IPFS/Arweave-Verwaltung wird hier implementiert...</p>
        </div>
      )}
      {activeTab === "settings" && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">System Einstellungen</h3>
          <p>Konfigurationsoptionen werden hier implementiert...</p>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;