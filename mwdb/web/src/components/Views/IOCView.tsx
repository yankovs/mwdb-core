/**
 * IOC View Component
 * Main view for displaying and managing IOCs
 */

import React, { useEffect, useState } from "react";
import {
  IOCCreateFormComponent,
  IOCDetailComponent,
  IOCListItemComponent,
  IOCStatsComponent,
  type IOC,
  type IOCStats,
} from "../IOC";

interface IOCViewProps {
  iocHash?: string; // If provided, shows detail view
}

export const IOCView: React.FC<IOCViewProps> = ({ iocHash }) => {
  const [ioc, setIOC] = useState<IOC | null>(null);
  const [iocs, setIOCs] = useState<IOC[]>([]);
  const [stats, setStats] = useState<IOCStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);

  // Fetch single IOC detail
  useEffect(() => {
    if (iocHash) {
      fetchIOCDetail();
    }
  }, [iocHash]);

  // Fetch IOC list and stats
  useEffect(() => {
    if (!iocHash) {
      fetchIOCList();
      fetchStats();
    }
  }, [iocHash]);

  const fetchIOCDetail = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`/api/ioc/${iocHash}`);
      if (!response.ok) throw new Error("Failed to fetch IOC");
      const data = await response.json();
      setIOC(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const fetchIOCList = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch("/api/ioc?count=50");
      if (!response.ok) throw new Error("Failed to fetch IOCs");
      const data = await response.json();
      setIOCs(data.iocs || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch("/api/ioc/stats");
      if (!response.ok) throw new Error("Failed to fetch stats");
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error("Failed to fetch IOC stats:", err);
    }
  };

  const handleCreateIOC = async (formData: Partial<IOC>) => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch("/api/ioc", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      if (!response.ok) throw new Error("Failed to create IOC");
      setShowCreateForm(false);
      await fetchIOCList();
      await fetchStats();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  if (iocHash && ioc) {
    return (
      <div className="container-fluid mt-4">
        <div className="row">
          <div className="col-md-12">
            <IOCDetailComponent ioc={ioc} />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid mt-4">
      <h2>IOCs (Indicators of Compromise)</h2>

      {error && <div className="alert alert-danger">{error}</div>}

      {stats && <IOCStatsComponent stats={stats} />}

      <div className="row mb-3">
        <div className="col-md-12">
          <button
            className="btn btn-primary"
            onClick={() => setShowCreateForm(!showCreateForm)}
          >
            {showCreateForm ? "Cancel" : "Add IOC"}
          </button>
        </div>
      </div>

      {showCreateForm && (
        <div className="row mb-3">
          <div className="col-md-6">
            <IOCCreateFormComponent onSubmit={handleCreateIOC} loading={loading} />
          </div>
        </div>
      )}

      {loading && !ioc && <div className="alert alert-info">Loading IOCs...</div>}

      {iocs.length > 0 ? (
        <div className="list-group">
          {iocs.map((ioc) => (
            <a
              key={ioc.dhash}
              href={`/ioc/${ioc.dhash}`}
              className="list-group-item list-group-item-action"
            >
              <IOCListItemComponent ioc={ioc} />
            </a>
          ))}
        </div>
      ) : (
        !loading && <div className="alert alert-info">No IOCs found.</div>
      )}
    </div>
  );
};

export default IOCView;
