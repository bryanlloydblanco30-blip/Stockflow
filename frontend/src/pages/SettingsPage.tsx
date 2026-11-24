import { useCallback, useEffect, useState } from "react";
import Shell from "../components/Shell";
import type { Navigate } from "../types";
import { api, type BackupFileDTO, type CategoryDTO, type SettingsDTO } from "../api";

export default function SettingsPage({ navigate }: { navigate: Navigate }) {
  const [settings, setSettings] = useState<SettingsDTO | null>(null);
  const [categories, setCategories] = useState<CategoryDTO[]>([]);
  const [backups, setBackups] = useState<BackupFileDTO[]>([]);
  const [banner, setBanner] = useState<{ type: "ok" | "error"; text: string } | null>(null);

  // Settings form
  const [storeName, setStoreName] = useState("");
  const [defaultWarn, setDefaultWarn] = useState("7");
  const [targetCover, setTargetCover] = useState("14");

  // New category form
  const [newCatName, setNewCatName] = useState("");
  const [newCatTracks, setNewCatTracks] = useState(true);
  const [newCatWarn, setNewCatWarn] = useState("7");

  const loadAll = useCallback(async () => {
    const [s, cats, bks] = await Promise.all([
      api.getSettings(),
      api.getCategories(),
      api.listBackups(),
    ]);
    setSettings(s);
    setStoreName(s.store_name);
    setDefaultWarn(String(s.default_warn_days));
    setTargetCover(String(s.target_cover_days));
    setCategories(cats);
    setBackups(bks.backups);
  }, []);

  useEffect(() => {
    loadAll().catch(() => {});
  }, [loadAll]);

  const handleSaveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.updateSettings({
        store_name: storeName.trim(),
        default_warn_days: parseInt(defaultWarn, 10) || 7,
        target_cover_days: parseInt(targetCover, 10) || 14,
      });
      setBanner({ type: "ok", text: "✓ Store settings saved." });
      await loadAll();
    } catch (err) {
      setBanner({ type: "error", text: err instanceof Error ? err.message : "Failed to save settings." });
    }
  };

  const handleAddCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCatName.trim()) return;
    try {
      await api.createCategory({
        name: newCatName.trim(),
        tracks_expiry: newCatTracks,
        warn_days: newCatTracks ? parseInt(newCatWarn, 10) || 7 : 0,
      });
      setNewCatName("");
      setBanner({ type: "ok", text: `✓ Category "${newCatName.trim()}" added.` });
      await loadAll();
    } catch (err) {
      setBanner({ type: "error", text: err instanceof Error ? err.message : "Failed to add category." });
    }
  };

  const handleToggleTracking = async (cat: CategoryDTO) => {
    try {
      await api.updateCategory(cat.id, {
        tracks_expiry: !cat.tracks_expiry,
        warn_days: !cat.tracks_expiry ? cat.warn_days || 7 : 0,
      });
      setBanner({
        type: "ok",
        text: `✓ Updated "${cat.name}" expiry tracking to ${!cat.tracks_expiry ? "ON" : "OFF"}.`,
      });
      await loadAll();
    } catch (err) {
      setBanner({ type: "error", text: err instanceof Error ? err.message : "Update failed." });
    }
  };

  const handleDeleteCategory = async (cat: CategoryDTO) => {
    try {
      const res = await api.deleteCategory(cat.id);
      setBanner({
        type: "ok",
        text: `✓ Deleted "${cat.name}". ${res.affected_products} product(s) moved to Uncategorized.`,
      });
      await loadAll();
    } catch (err) {
      setBanner({ type: "error", text: err instanceof Error ? err.message : "Delete failed." });
    }
  };

  const handleExportBackup = async () => {
    try {
      const res = await api.exportBackup();
      setBanner({ type: "ok", text: `✓ Backup exported: ${res.filename} (${(res.size_bytes / 1024).toFixed(1)} KB).` });
      await loadAll();
    } catch (err) {
      setBanner({ type: "error", text: err instanceof Error ? err.message : "Backup export failed." });
    }
  };

  const handleRestoreBackup = async (filename: string) => {
    if (!window.confirm(`Restore database from "${filename}"? Current unsaved changes will be replaced.`)) {
      return;
    }
    try {
      const res = await api.restoreBackup(filename);
      setBanner({
        type: "ok",
        text: `✓ Restored "${res.restored}" (${res.products_loaded} products loaded into memory).`,
      });
      await loadAll();
    } catch (err) {
      setBanner({ type: "error", text: err instanceof Error ? err.message : "Restore failed." });
    }
  };

  return (
    <Shell
      active="home"
      page="settings"
      title="Settings, Categories & Backup"
      subtitle="Configure store defaults, expiry warning windows, and SQLite backups"
      navigate={navigate}
      action={
        <button className="primary blue" onClick={handleExportBackup}>
          Export Backup Now
        </button>
      }
    >
      {banner && (
        <div
          style={{
            padding: "10px 16px",
            borderRadius: "12px",
            marginBottom: "14px",
            fontWeight: 600,
            background: banner.type === "ok" ? "#e5efdb" : "#fee2e2",
            color: banner.type === "ok" ? "#245c45" : "#991b1b",
          }}
        >
          {banner.text}
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "18px", marginBottom: "18px" }}>
        {/* Store Settings */}
        <section className="panel" style={{ padding: "20px" }}>
          <h2 style={{ marginTop: 0 }}>Store Defaults</h2>
          <form onSubmit={handleSaveSettings} className="modal-form">
            <div className="form-field">
              <label>Store Name</label>
              <input value={storeName} onChange={(e) => setStoreName(e.target.value)} required />
            </div>
            <div className="form-field">
              <label>Default Uncategorized Warning Days</label>
              <input type="number" min="1" value={defaultWarn} onChange={(e) => setDefaultWarn(e.target.value)} />
            </div>
            <div className="form-field">
              <label>Target Days of Cover (Restock)</label>
              <input type="number" min="1" value={targetCover} onChange={(e) => setTargetCover(e.target.value)} />
            </div>
            <small style={{ color: "#69756b" }}>Database path: <code>{settings?.db_path ?? "—"}</code></small>
            <button type="submit" className="btn-submit" style={{ marginTop: "8px" }}>
              Save Defaults
            </button>
          </form>
        </section>

        {/* Backup & Restore */}
        <section className="panel" style={{ padding: "20px" }}>
          <h2 style={{ marginTop: 0 }}>Database Backups</h2>
          <p style={{ fontSize: "14px", color: "#69756b" }}>
            Export a point-in-time copy of your offline SQLite database or restore an earlier snapshot.
          </p>
          <div className="table-scroll" style={{ maxHeight: "220px" }}>
            {backups.length === 0 ? (
              <p style={{ color: "#69756b" }}>No backups exported yet. Click "Export Backup Now" above.</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Filename</th>
                    <th>Size</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {backups.map((b) => (
                    <tr key={b.filename}>
                      <td><code>{b.filename}</code></td>
                      <td>{(b.size_bytes / 1024).toFixed(1)} KB</td>
                      <td style={{ textAlign: "right" }}>
                        <button className="purple-pill small" onClick={() => handleRestoreBackup(b.filename)}>
                          Restore
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </section>
      </div>

      {/* Category Management */}
      <section className="panel table-panel" style={{ padding: "20px" }}>
        <h2 style={{ marginTop: 0 }}>Categories & Expiry Windows</h2>
        <form
          onSubmit={handleAddCategory}
          style={{ display: "flex", gap: "10px", flexWrap: "wrap", alignItems: "center", marginBottom: "14px" }}
        >
          <input
            placeholder="New category name"
            value={newCatName}
            onChange={(e) => setNewCatName(e.target.value)}
            required
            style={{ padding: "10px 14px", borderRadius: "12px", border: "1px solid #dce3d6" }}
          />
          <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "14px" }}>
            <input
              type="checkbox"
              checked={newCatTracks}
              onChange={(e) => setNewCatTracks(e.target.checked)}
            />
            Tracks expiry
          </label>
          {newCatTracks && (
            <input
              type="number"
              min="1"
              value={newCatWarn}
              onChange={(e) => setNewCatWarn(e.target.value)}
              style={{ width: "90px", padding: "10px 12px", borderRadius: "12px", border: "1px solid #dce3d6" }}
              title="Amber warning days"
            />
          )}
          <button type="submit" className="blue-pill">
            + Add Category
          </button>
        </form>

        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Category</th>
                <th>Tracks Expiry</th>
                <th>Amber Window</th>
                <th>Red Limit (1/3)</th>
                <th style={{ textAlign: "right" }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {categories.map((c) => (
                <tr key={c.id}>
                  <td><strong>{c.name}</strong></td>
                  <td>
                    <span className={`badge ${c.tracks_expiry ? "green" : "amber"}`}>
                      {c.tracks_expiry ? "Yes (FEFO)" : "No (FIFO)"}
                    </span>
                  </td>
                  <td>{c.tracks_expiry ? `${c.warn_days} days` : "—"}</td>
                  <td>{c.tracks_expiry ? `${c.red_days} days` : "—"}</td>
                  <td style={{ textAlign: "right", whiteSpace: "nowrap" }}>
                    <button
                      className="restock-row-btn"
                      style={{ marginRight: "6px" }}
                      onClick={() => handleToggleTracking(c)}
                    >
                      Toggle Tracking
                    </button>
                    <button className="purple-pill small" onClick={() => handleDeleteCategory(c)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </Shell>
  );
}
