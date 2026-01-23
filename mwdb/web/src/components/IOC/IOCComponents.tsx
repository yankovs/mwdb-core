/*
 * IOC Components - React/TypeScript components for displaying IOCs
 */

import React from "react";

/**
 * Types for IOC components
 */
export interface IOC {
  id: string;
  type: "ioc";
  dhash: string;
  ioc_type: string;
  value: string;
  severity: "low" | "medium" | "high" | "critical";
  source?: string;
  is_active: boolean;
  last_seen?: string;
  upload_time: string;
  tags: Array<{
    tag: string;
    auto: boolean;
  }>;
}

export interface IOCListItem extends IOC {}

export interface IOCStats {
  total: number;
  by_type: Record<string, number>;
  by_severity: Record<string, number>;
  active: number;
}

/**
 * IOC Type Badge Component
 * Displays the IOC type with color coding
 */
export const IOCTypeBadge: React.FC<{ type: string }> = ({ type }) => {
  const typeColors: Record<string, string> = {
    ip: "badge-primary",
    iprange: "badge-info",
    url: "badge-warning",
    domain: "badge-warning",
    email: "badge-info",
    md5: "badge-secondary",
    sha1: "badge-secondary",
    sha256: "badge-secondary",
    sha512: "badge-secondary",
    ssdeep: "badge-secondary",
    file_path: "badge-light",
    registry_key: "badge-light",
    c2_url: "badge-danger",
    mutex: "badge-info",
    process_name: "badge-light",
  };

  return (
    <span className={`badge ${typeColors[type] || "badge-dark"}`}>
      {type.toUpperCase()}
    </span>
  );
};

/**
 * IOC Severity Badge Component
 * Displays severity with color coding
 */
export const IOCSeverityBadge: React.FC<{ severity: string }> = ({
  severity,
}) => {
  const severityColors: Record<string, string> = {
    low: "badge-success",
    medium: "badge-warning",
    high: "badge-danger",
    critical: "badge-dark",
  };

  return (
    <span className={`badge ${severityColors[severity] || "badge-secondary"}`}>
      {severity.toUpperCase()}
    </span>
  );
};

/**
 * IOC List Item Component
 * Displays a single IOC in a list view
 */
export const IOCListItemComponent: React.FC<{ ioc: IOCListItem }> = ({
  ioc,
}) => {
  return (
    <div className="list-group-item">
      <div className="d-flex justify-content-between align-items-start">
        <div className="flex-grow-1">
          <div className="d-flex gap-2 mb-2">
            <IOCTypeBadge type={ioc.ioc_type} />
            <IOCSeverityBadge severity={ioc.severity} />
          </div>
          <code className="user-select-all">{ioc.value}</code>
          {ioc.source && <div className="small text-muted">Source: {ioc.source}</div>}
          {ioc.last_seen && (
            <div className="small text-muted">Last seen: {ioc.last_seen}</div>
          )}
        </div>
        <div className="text-right">
          {ioc.is_active ? (
            <span className="badge badge-success">Active</span>
          ) : (
            <span className="badge badge-secondary">Inactive</span>
          )}
        </div>
      </div>
    </div>
  );
};

/**
 * IOC Detail Component
 * Displays full details of a single IOC
 */
export const IOCDetailComponent: React.FC<{ ioc: IOC }> = ({ ioc }) => {
  return (
    <div className="card">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-start mb-3">
          <div>
            <h4 className="card-title">
              <code className="user-select-all">{ioc.value}</code>
            </h4>
            <div className="d-flex gap-2">
              <IOCTypeBadge type={ioc.ioc_type} />
              <IOCSeverityBadge severity={ioc.severity} />
              {ioc.is_active ? (
                <span className="badge badge-success">Active</span>
              ) : (
                <span className="badge badge-secondary">Inactive</span>
              )}
            </div>
          </div>
        </div>

        <table className="table table-sm">
          <tbody>
            <tr>
              <td className="font-weight-bold">IOC Type:</td>
              <td>{ioc.ioc_type}</td>
            </tr>
            <tr>
              <td className="font-weight-bold">Value:</td>
              <td>
                <code className="user-select-all">{ioc.value}</code>
              </td>
            </tr>
            <tr>
              <td className="font-weight-bold">Severity:</td>
              <td>
                <IOCSeverityBadge severity={ioc.severity} />
              </td>
            </tr>
            {ioc.source && (
              <tr>
                <td className="font-weight-bold">Source:</td>
                <td>{ioc.source}</td>
              </tr>
            )}
            <tr>
              <td className="font-weight-bold">Status:</td>
              <td>
                {ioc.is_active ? (
                  <span className="badge badge-success">Active</span>
                ) : (
                  <span className="badge badge-secondary">Inactive</span>
                )}
              </td>
            </tr>
            <tr>
              <td className="font-weight-bold">Uploaded:</td>
              <td>{new Date(ioc.upload_time).toLocaleString()}</td>
            </tr>
            {ioc.last_seen && (
              <tr>
                <td className="font-weight-bold">Last Seen:</td>
                <td>{new Date(ioc.last_seen).toLocaleString()}</td>
              </tr>
            )}
            <tr>
              <td className="font-weight-bold">Hash:</td>
              <td>
                <code className="user-select-all text-monospace">{ioc.dhash}</code>
              </td>
            </tr>
          </tbody>
        </table>

        {ioc.tags && ioc.tags.length > 0 && (
          <div className="mt-3">
            <h6>Tags:</h6>
            <div className="d-flex flex-wrap gap-1">
              {ioc.tags.map((tag) => (
                <span
                  key={tag.tag}
                  className={`badge ${tag.auto ? "badge-secondary" : "badge-primary"}`}
                >
                  {tag.tag}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * IOC Create Form Component
 * Form for creating new IOCs with auto-detection
 */
export const IOCCreateFormComponent: React.FC<{
  onSubmit: (data: Partial<IOC>) => void;
  loading?: boolean;
}> = ({ onSubmit, loading = false }) => {
  const [formData, setFormData] = React.useState<Partial<IOC>>({
    ioc_type: "",
    value: "",
    severity: "medium",
    source: "",
    is_active: true,
  });

  const [detectedType, setDetectedType] = React.useState<string | null>(null);

  const handleValueChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setFormData({ ...formData, value });

    // Auto-detect IOC type
    if (value.trim()) {
      try {
        const response = await fetch("/api/ioc/auto_detect", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ value }),
        });
        const data = await response.json();
        setDetectedType(data.detected_type);
        if (data.detected_type && !formData.ioc_type) {
          setFormData((prev) => ({ ...prev, ioc_type: data.detected_type }));
        }
      } catch (error) {
        console.error("Failed to auto-detect IOC type:", error);
      }
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="ioc_value">IOC Value *</label>
        <input
          id="ioc_value"
          type="text"
          className="form-control"
          placeholder="Enter IP, URL, domain, hash, etc."
          value={formData.value || ""}
          onChange={handleValueChange}
          required
          disabled={loading}
        />
        {detectedType && (
          <small className="form-text text-muted">
            Detected: <IOCTypeBadge type={detectedType} />
          </small>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="ioc_type">IOC Type *</label>
        <select
          id="ioc_type"
          className="form-control"
          value={formData.ioc_type || ""}
          onChange={(e) => setFormData({ ...formData, ioc_type: e.target.value })}
          required
          disabled={loading}
        >
          <option value="">Select a type...</option>
          <optgroup label="Network">
            <option value="ip">IPv4/IPv6 Address</option>
            <option value="iprange">IP Range (CIDR)</option>
            <option value="url">URL</option>
            <option value="domain">Domain</option>
            <option value="email">Email Address</option>
            <option value="c2_url">C2 URL</option>
          </optgroup>
          <optgroup label="Hash">
            <option value="md5">MD5</option>
            <option value="sha1">SHA1</option>
            <option value="sha256">SHA256</option>
            <option value="sha512">SHA512</option>
            <option value="ssdeep">SSDEEP</option>
          </optgroup>
          <optgroup label="File System">
            <option value="file_path">File Path</option>
            <option value="registry_key">Registry Key</option>
          </optgroup>
          <optgroup label="Process">
            <option value="process_name">Process Name</option>
            <option value="mutex">Mutex</option>
          </optgroup>
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="severity">Severity</label>
        <select
          id="severity"
          className="form-control"
          value={formData.severity || "medium"}
          onChange={(e) => setFormData({ ...formData, severity: e.target.value as any })}
          disabled={loading}
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="source">Source</label>
        <input
          id="source"
          type="text"
          className="form-control"
          placeholder="e.g., threat_feed_name"
          value={formData.source || ""}
          onChange={(e) => setFormData({ ...formData, source: e.target.value })}
          disabled={loading}
        />
      </div>

      <div className="form-check">
        <input
          id="is_active"
          type="checkbox"
          className="form-check-input"
          checked={formData.is_active ?? true}
          onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
          disabled={loading}
        />
        <label className="form-check-label" htmlFor="is_active">
          Active
        </label>
      </div>

      <button
        type="submit"
        className="btn btn-primary mt-3"
        disabled={loading}
      >
        {loading ? "Creating..." : "Create IOC"}
      </button>
    </form>
  );
};

/**
 * IOC Statistics Component
 * Displays IOC statistics dashboard
 */
export const IOCStatsComponent: React.FC<{ stats: IOCStats }> = ({ stats }) => {
  return (
    <div className="row mb-3">
      <div className="col-md-3">
        <div className="card text-center">
          <div className="card-body">
            <h5 className="card-title">Total IOCs</h5>
            <h3 className="text-primary">{stats.total}</h3>
          </div>
        </div>
      </div>
      <div className="col-md-3">
        <div className="card text-center">
          <div className="card-body">
            <h5 className="card-title">Active</h5>
            <h3 className="text-success">{stats.active}</h3>
          </div>
        </div>
      </div>
      <div className="col-md-6">
        <div className="card">
          <div className="card-body">
            <h5 className="card-title">By Type</h5>
            {Object.entries(stats.by_type)
              .sort(([, a], [, b]) => b - a)
              .slice(0, 5)
              .map(([type, count]) => (
                <div key={type} className="d-flex justify-content-between">
                  <span>{type}</span>
                  <strong>{count}</strong>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  );
};
