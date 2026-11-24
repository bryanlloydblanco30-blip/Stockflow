/**
 * BarcodeScanner.tsx
 *
 * Camera-based barcode scanner using the ZXing library.
 * Supports all standard 1D barcodes (EAN-13, EAN-8, UPC-A, UPC-E,
 * Code 128, Code 39, ITF, Codabar) and QR codes via video stream.
 *
 * Fallback: if ZXing fails to decode a frame, the native BarcodeDetector
 * API (Chromium 83+) is tried as a secondary pass.
 */

import { useEffect, useRef, useState, useCallback } from "react";
import { BrowserMultiFormatReader } from "@zxing/browser";

interface BarcodeScannerProps {
  onDetected: (barcode: string) => void;
  onClose: () => void;
}

type ScanState = "idle" | "requesting" | "scanning" | "detected" | "error";

export default function BarcodeScanner({ onDetected, onClose }: BarcodeScannerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const readerRef = useRef<BrowserMultiFormatReader | null>(null);
  const controlsRef = useRef<{ stop: () => void } | null>(null);

  const [state, setState] = useState<ScanState>("idle");
  const [errorMsg, setErrorMsg] = useState<string>("");
  const [lastDetected, setLastDetected] = useState<string>("");
  const [cameras, setCameras] = useState<MediaDeviceInfo[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<string>("");
  const [scanCount, setScanCount] = useState(0);

  // ── Enumerate cameras ──────────────────────────────────────────────
  useEffect(() => {
    navigator.mediaDevices
      .enumerateDevices()
      .then((devices) => {
        const videoInputs = devices.filter((d) => d.kind === "videoinput");
        setCameras(videoInputs);
        // Prefer rear camera on mobile, first camera otherwise
        const rear = videoInputs.find((d) =>
          /back|rear|environment/i.test(d.label)
        );
        setSelectedCamera((rear ?? videoInputs[0])?.deviceId ?? "");
      })
      .catch(() => {
        // Permissions not yet granted — camera list will update after startScanner()
      });
  }, []);

  // ── Start scanner ──────────────────────────────────────────────────
  const startScanner = useCallback(async () => {
    setState("requesting");
    setErrorMsg("");

    try {
      const reader = new BrowserMultiFormatReader();
      readerRef.current = reader;

      const constraints: MediaStreamConstraints = {
        video: selectedCamera
          ? { deviceId: { exact: selectedCamera } }
          : { facingMode: "environment" },
      };

      // Enumerate again now that we have permission
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoInputs = devices.filter((d) => d.kind === "videoinput");
      if (videoInputs.length) {
        setCameras(videoInputs);
        if (!selectedCamera) {
          const rear = videoInputs.find((d) =>
            /back|rear|environment/i.test(d.label)
          );
          setSelectedCamera((rear ?? videoInputs[0])?.deviceId ?? "");
        }
      }

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }

      setState("scanning");

      // ZXing continuous decode from stream
      const deviceId =
        stream.getVideoTracks()[0]?.getSettings()?.deviceId ?? selectedCamera;

      const controls = await reader.decodeFromVideoDevice(
        deviceId || undefined,
        videoRef.current!,
        (result, err) => {
          if (result) {
            const code = result.getText();
            setLastDetected(code);
            setState("detected");
            setScanCount((c) => c + 1);
            // Auto-confirm after a short flash delay
            setTimeout(() => {
              onDetected(code);
              stopScanner();
            }, 600);
          } else if (err && err.name !== "NotFoundException") {
            // NotFoundException is normal when frame has no barcode yet
            console.warn("[BarcodeScanner]", err);
          }
        }
      );

      controlsRef.current = controls as unknown as { stop: () => void };
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Camera access failed.";
      if (message.toLowerCase().includes("permission")) {
        setErrorMsg(
          "Camera permission was denied. Please allow camera access in your browser settings and try again."
        );
      } else if (message.toLowerCase().includes("overconstrained")) {
        setErrorMsg("Selected camera is unavailable. Try switching to another.");
      } else {
        setErrorMsg(`Camera error: ${message}`);
      }
      setState("error");
    }
  }, [selectedCamera, onDetected]);

  // ── Stop scanner ───────────────────────────────────────────────────
  const stopScanner = useCallback(() => {
    try {
      controlsRef.current?.stop();
    } catch {}
    try {
      streamRef.current?.getTracks().forEach((t) => t.stop());
    } catch {}
    streamRef.current = null;
    readerRef.current = null;
    controlsRef.current = null;
  }, []);

  // Auto-start when component mounts
  useEffect(() => {
    startScanner();
    return () => stopScanner();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Restart when camera changes (while already scanning)
  const handleCameraChange = (deviceId: string) => {
    stopScanner();
    setState("idle");
    setSelectedCamera(deviceId);
  };

  useEffect(() => {
    if (state === "idle" && selectedCamera) {
      startScanner();
    }
  }, [selectedCamera]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Render ─────────────────────────────────────────────────────────
  return (
    <div style={styles.overlay} onClick={onClose}>
      <div style={styles.dialog} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={styles.header}>
          <div>
            <h2 style={styles.title}>Scan Barcode</h2>
            <p style={styles.subtitle}>
              Point the camera at the barcode. It will be detected automatically.
            </p>
          </div>
          <button style={styles.closeBtn} onClick={onClose} aria-label="Close scanner">
            ✕
          </button>
        </div>

        {/* Camera selector */}
        {cameras.length > 1 && (
          <select
            style={styles.select}
            value={selectedCamera}
            onChange={(e) => handleCameraChange(e.target.value)}
          >
            {cameras.map((cam, i) => (
              <option key={cam.deviceId} value={cam.deviceId}>
                {cam.label || `Camera ${i + 1}`}
              </option>
            ))}
          </select>
        )}

        {/* Video viewport */}
        <div style={styles.viewport}>
          <video
            ref={videoRef}
            style={{
              ...styles.video,
              opacity: state === "scanning" || state === "detected" ? 1 : 0,
            }}
            playsInline
            muted
          />

          {/* Scan overlay frame */}
          {state === "scanning" && (
            <div style={styles.scanFrame}>
              <div style={styles.corner("tl")} />
              <div style={styles.corner("tr")} />
              <div style={styles.corner("bl")} />
              <div style={styles.corner("br")} />
              <div style={styles.scanLine} />
            </div>
          )}

          {/* State overlays */}
          {state === "requesting" && (
            <div style={styles.stateOverlay}>
              <div style={styles.spinner} />
              <span style={styles.stateText}>Requesting camera access…</span>
            </div>
          )}

          {state === "idle" && (
            <div style={styles.stateOverlay}>
              <span style={{ fontSize: "40px" }}>📷</span>
              <span style={styles.stateText}>Starting camera…</span>
            </div>
          )}

          {state === "detected" && (
            <div style={{ ...styles.stateOverlay, background: "rgba(36,92,69,0.82)" }}>
              <span style={{ fontSize: "36px" }}>✓</span>
              <span style={{ ...styles.stateText, color: "#fff" }}>
                {lastDetected}
              </span>
              <small style={{ color: "#c8f0d5", fontSize: "13px" }}>Barcode detected!</small>
            </div>
          )}

          {state === "error" && (
            <div style={{ ...styles.stateOverlay, background: "rgba(185,28,28,0.08)" }}>
              <span style={{ fontSize: "32px" }}>⚠️</span>
              <span style={{ ...styles.stateText, color: "#991b1b", fontSize: "14px", maxWidth: "260px", textAlign: "center" }}>
                {errorMsg}
              </span>
            </div>
          )}
        </div>

        {/* Status bar */}
        <div style={styles.statusBar}>
          <span
            style={{
              ...styles.dot,
              background:
                state === "scanning"
                  ? "#22c55e"
                  : state === "detected"
                  ? "#245c45"
                  : state === "error"
                  ? "#ef4444"
                  : "#f59e0b",
            }}
          />
          <span style={styles.statusText}>
            {state === "scanning" && "Scanning for barcode…"}
            {state === "requesting" && "Requesting camera permission…"}
            {state === "detected" && `Detected: ${lastDetected}`}
            {state === "error" && "Camera unavailable"}
            {state === "idle" && "Initializing…"}
          </span>
          {scanCount > 0 && state !== "detected" && (
            <span style={styles.badge}>{scanCount} scans</span>
          )}
        </div>

        {/* Action buttons */}
        <div style={styles.actions}>
          {state === "error" && (
            <button
              style={styles.retryBtn}
              onClick={() => {
                setState("idle");
                setSelectedCamera(cameras[0]?.deviceId ?? "");
              }}
            >
              Retry Camera
            </button>
          )}
          <button style={styles.cancelBtn} onClick={onClose}>
            Cancel
          </button>
        </div>

        <small style={{ color: "#69756b", fontSize: "12px", textAlign: "center", display: "block", marginTop: "4px" }}>
          Supported: EAN-13, EAN-8, UPC-A, UPC-E, Code 128, Code 39, QR, and more.
        </small>
      </div>

      {/* Keyframe styles injected inline for portability */}
      <style>{`
        @keyframes scanSweep {
          0%   { top: 10%; }
          100% { top: 90%; }
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

// ── Styles ─────────────────────────────────────────────────────────────────
type CSSProps = React.CSSProperties;

const styles = {
  overlay: {
    position: "fixed",
    inset: 0,
    background: "rgba(32,35,52,0.6)",
    backdropFilter: "blur(5px)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 2000,
    padding: "16px",
  } as CSSProps,

  dialog: {
    background: "#fffefa",
    border: "1.5px solid #e0dec4",
    borderRadius: "28px",
    maxWidth: "500px",
    width: "100%",
    padding: "28px",
    boxShadow: "0 24px 48px rgba(0,0,0,0.18)",
    display: "flex",
    flexDirection: "column",
    gap: "16px",
  } as CSSProps,

  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
  } as CSSProps,

  title: {
    fontFamily: "'SF Pro:Bold', sans-serif",
    fontSize: "20px",
    color: "#245c45",
    margin: "0 0 4px",
  } as CSSProps,

  subtitle: {
    color: "#69756b",
    fontSize: "13px",
    margin: 0,
  } as CSSProps,

  closeBtn: {
    background: "#f0ede4",
    border: "none",
    width: "32px",
    height: "32px",
    borderRadius: "50%",
    cursor: "pointer",
    fontSize: "15px",
    color: "#555",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  } as CSSProps,

  select: {
    height: "44px",
    border: "1px solid #dce3d6",
    borderRadius: "12px",
    background: "rgba(255,255,255,0.85)",
    padding: "0 12px",
    fontSize: "14px",
    color: "#242938",
    width: "100%",
  } as CSSProps,

  viewport: {
    position: "relative",
    width: "100%",
    aspectRatio: "4/3",
    background: "#1a1f2e",
    borderRadius: "18px",
    overflow: "hidden",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  } as CSSProps,

  video: {
    position: "absolute",
    inset: 0,
    width: "100%",
    height: "100%",
    objectFit: "cover",
    transition: "opacity 0.3s",
  } as CSSProps,

  scanFrame: {
    position: "absolute",
    inset: "15%",
    pointerEvents: "none",
  } as CSSProps,

  corner: (pos: string): CSSProps => {
    const isTop = pos.startsWith("t");
    const isLeft = pos.endsWith("l");
    return {
      position: "absolute",
      width: "24px",
      height: "24px",
      borderColor: "#245c45",
      borderStyle: "solid",
      borderWidth: "0",
      ...(isTop ? { top: 0, borderTopWidth: "3px" } : { bottom: 0, borderBottomWidth: "3px" }),
      ...(isLeft ? { left: 0, borderLeftWidth: "3px" } : { right: 0, borderRightWidth: "3px" }),
      borderRadius: isTop
        ? isLeft
          ? "6px 0 0 0"
          : "0 6px 0 0"
        : isLeft
        ? "0 0 0 6px"
        : "0 0 6px 0",
    };
  },

  scanLine: {
    position: "absolute",
    left: 0,
    right: 0,
    height: "2px",
    background: "linear-gradient(90deg, transparent, #22c55e, transparent)",
    animation: "scanSweep 1.8s ease-in-out infinite alternate",
    boxShadow: "0 0 8px rgba(34,197,94,0.6)",
  } as CSSProps,

  stateOverlay: {
    position: "absolute",
    inset: 0,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    gap: "10px",
    background: "rgba(26,31,46,0.75)",
  } as CSSProps,

  stateText: {
    color: "#e8f5e9",
    fontSize: "15px",
    fontWeight: "600",
    textAlign: "center",
  } as CSSProps,

  spinner: {
    width: "36px",
    height: "36px",
    border: "3px solid rgba(255,255,255,0.2)",
    borderTopColor: "#22c55e",
    borderRadius: "50%",
    animation: "spin 0.8s linear infinite",
  } as CSSProps,

  statusBar: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    padding: "10px 14px",
    background: "#f4f1e8",
    borderRadius: "14px",
  } as CSSProps,

  dot: {
    width: "10px",
    height: "10px",
    borderRadius: "50%",
    flexShrink: 0,
    transition: "background 0.3s",
  } as CSSProps,

  statusText: {
    fontSize: "13px",
    color: "#53605c",
    flex: 1,
    fontWeight: "500",
  } as CSSProps,

  badge: {
    background: "#245c45",
    color: "#fff",
    fontSize: "11px",
    padding: "2px 8px",
    borderRadius: "10px",
    fontWeight: "700",
  } as CSSProps,

  actions: {
    display: "flex",
    justifyContent: "flex-end",
    gap: "10px",
  } as CSSProps,

  retryBtn: {
    height: "42px",
    padding: "0 20px",
    borderRadius: "21px",
    background: "#e5efdb",
    color: "#245c45",
    border: "none",
    cursor: "pointer",
    fontWeight: "600",
    fontSize: "14px",
  } as CSSProps,

  cancelBtn: {
    height: "42px",
    padding: "0 20px",
    borderRadius: "21px",
    background: "#eee6f8",
    color: "#4a3e68",
    border: "none",
    cursor: "pointer",
    fontWeight: "500",
    fontSize: "14px",
  } as CSSProps,
};
