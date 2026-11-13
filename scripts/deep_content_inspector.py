import os
import json
import subprocess
import glob

OUTPUT_DIR = "./storage/output"
SNAPSHOT_DIR = "./storage/qa_inspection_snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

def run_cmd(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.stdout, p.stderr, p.returncode

def inspect_video_stream(file_path):
    # Probe streams
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,size,bit_rate:stream=index,codec_type,codec_name,duration,width,height,r_frame_rate,pix_fmt,sample_rate,channels,bit_rate,start_time",
        "-of", "json", file_path
    ]
    stdout, _, _ = run_cmd(cmd)
    try:
        data = json.loads(stdout)
    except Exception:
        return {"error": "ffprobe json parse failed"}

    v_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), None)
    a_stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
    fmt = data.get("format", {})

    # Black frame detection
    black_cmd = [
        "ffmpeg", "-i", file_path,
        "-vf", "blackdetect=d=1.0:pix_th=0.10",
        "-an", "-f", "null", "-"
    ]
    _, black_err, _ = run_cmd(black_cmd)
    black_frames = [line for line in black_err.splitlines() if "black_start" in line]

    # Audio Loudness (EBU R128)
    loud_cmd = [
        "ffmpeg", "-i", file_path,
        "-af", "ebur128",
        "-vn", "-f", "null", "-"
    ]
    _, loud_err, _ = run_cmd(loud_cmd)
    
    i_lufs = None
    lra = None
    for line in loud_err.splitlines():
        if "I:" in line and "LUFS" in line and i_lufs is None:
            parts = line.strip().split()
            for idx, p in enumerate(parts):
                if p == "I:":
                    i_lufs = parts[idx+1]
        if "LRA:" in line and "LU" in line and lra is None:
            parts = line.strip().split()
            for idx, p in enumerate(parts):
                if p == "LRA:":
                    lra = parts[idx+1]

    # Silence detection
    silence_cmd = [
        "ffmpeg", "-i", file_path,
        "-af", "silencedetect=noise=-30dB:d=1.5",
        "-vn", "-f", "null", "-"
    ]
    _, sil_err, _ = run_cmd(silence_cmd)
    silence_periods = [l for l in sil_err.splitlines() if "silence_start" in l]

    # Extract snapshots for visual review
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    ep_name = os.path.basename(os.path.dirname(file_path))
    v_dur = float(v_stream.get("duration", 0.0)) if v_stream else 0.0
    a_dur = float(a_stream.get("duration", 0.0)) if a_stream else 0.0
    total_dur = float(fmt.get("duration", 0.0))

    snapshots = []
    if v_dur > 2.0:
        times = [round(v_dur * 0.2, 1), round(v_dur * 0.5, 1), round(v_dur * 0.8, 1)]
        for t in times:
            snap_path = os.path.join(SNAPSHOT_DIR, f"{ep_name}_{base_name}_t{t}s.jpg")
            snap_cmd = [
                "ffmpeg", "-y", "-ss", str(t),
                "-i", file_path,
                "-vframes", "1", "-q:v", "3",
                snap_path
            ]
            run_cmd(snap_cmd)
            if os.path.exists(snap_path):
                snapshots.append(snap_path)

    # Calculate sync drift
    sync_drift_ms = abs(v_dur - a_dur) * 1000.0 if (v_dur > 0 and a_dur > 0) else 0.0

    return {
        "file": file_path,
        "format": {
            "duration_seconds": round(total_dur, 2),
            "file_size_bytes": int(fmt.get("size", 0)),
            "bitrate_kbps": round(float(fmt.get("bit_rate", 0))/1000.0, 1)
        },
        "video": {
            "codec": v_stream.get("codec_name") if v_stream else None,
            "resolution": f"{v_stream.get('width')}x{v_stream.get('height')}" if v_stream else None,
            "fps": v_stream.get("r_frame_rate") if v_stream else None,
            "duration_seconds": round(v_dur, 2),
            "bitrate_kbps": round(float(v_stream.get("bit_rate", 0))/1000.0, 1) if v_stream and v_stream.get("bit_rate") else None,
            "pix_fmt": v_stream.get("pix_fmt") if v_stream else None,
            "black_segments_count": len(black_frames),
            "black_segments": black_frames[:3]
        },
        "audio": {
            "codec": a_stream.get("codec_name") if a_stream else None,
            "sample_rate_hz": a_stream.get("sample_rate") if a_stream else None,
            "channels": a_stream.get("channels") if a_stream else None,
            "duration_seconds": round(a_dur, 2),
            "bitrate_kbps": round(float(a_stream.get("bit_rate", 0))/1000.0, 1) if a_stream and a_stream.get("bit_rate") else None,
            "integrated_loudness_lufs": i_lufs,
            "loudness_range_lra": lra,
            "silence_intervals_gt_1_5s": len(silence_periods)
        },
        "av_sync": {
            "drift_ms": round(sync_drift_ms, 1),
            "sync_healthy": sync_drift_ms < 250.0,
            "video_start_time": v_stream.get("start_time") if v_stream else None,
            "audio_start_time": a_stream.get("start_time") if a_stream else None
        },
        "snapshots": snapshots
    }

def main():
    episodes = sorted([d for d in os.listdir(OUTPUT_DIR) if os.path.isdir(os.path.join(OUTPUT_DIR, d))])
    all_reports = []

    for ep in episodes:
        ep_dir = os.path.join(OUTPUT_DIR, ep)
        for f in sorted(os.listdir(ep_dir)):
            if f.endswith(".mp4") and (f.startswith("master_16x9") or f.startswith("social_9x16")):
                fp = os.path.join(ep_dir, f)
                rep = inspect_video_stream(fp)
                rep["episode_id"] = ep
                rep["variant"] = "16:9 Landscape Master" if "16x9" in f else "9:16 Social Reel"
                all_reports.append(rep)

    report_path = "./storage/qa_inspection_report.json"
    with open(report_path, "w", encoding="utf-8") as rf:
        json.dump(all_reports, rf, indent=2)

    print(f"Inspection complete. Evaluated {len(all_reports)} deliverables. Report saved to {report_path}")

if __name__ == "__main__":
    main()
