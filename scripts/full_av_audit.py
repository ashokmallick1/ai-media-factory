import os
import glob
import json
import subprocess

def inspect_all():
    files = glob.glob('./storage/output/*/*.mp4')
    results = []
    print(f"Inspecting {len(files)} files...")
    for f in sorted(files):
        cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size,bit_rate:stream=index,codec_type,codec_name,duration,width,height,r_frame_rate,sample_rate,channels,bit_rate', '-of', 'json', f]
        p = subprocess.run(cmd, capture_output=True, text=True)
        try:
            data = json.loads(p.stdout)
        except Exception:
            continue
        v = next((s for s in data.get('streams', []) if s.get('codec_type') == 'video'), {})
        a = next((s for s in data.get('streams', []) if s.get('codec_type') == 'audio'), {})
        fmt = data.get('format', {})
        
        # ebur128 summary
        cmd_loud = ['ffmpeg', '-i', f, '-af', 'ebur128', '-vn', '-f', 'null', '-']
        p_loud = subprocess.run(cmd_loud, capture_output=True, text=True)
        lines = p_loud.stderr.splitlines()
        i_lufs, lra, tp = 'N/A', 'N/A', 'N/A'
        for idx, line in enumerate(lines):
            if 'Integrated loudness:' in line and idx + 1 < len(lines):
                parts = lines[idx+1].strip().split()
                if len(parts) >= 2:
                    i_lufs = parts[1]
            if 'Loudness range:' in line and idx + 1 < len(lines):
                parts = lines[idx+1].strip().split()
                if len(parts) >= 2:
                    lra = parts[1]
            if 'True peak:' in line and idx + 1 < len(lines):
                parts = lines[idx+1].strip().split()
                if len(parts) >= 2:
                    tp = parts[1]
                
        # drift
        vd = float(v.get('duration', 0.0))
        ad = float(a.get('duration', 0.0))
        drift = abs(vd - ad) * 1000 if vd > 0 and ad > 0 else 0
        
        # black frames
        cmd_black = ['ffmpeg', '-i', f, '-vf', 'blackdetect=d=1.0:pix_th=0.10', '-an', '-f', 'null', '-']
        p_black = subprocess.run(cmd_black, capture_output=True, text=True)
        black_cnt = len([l for l in p_black.stderr.splitlines() if 'black_start' in l])

        results.append({
            'file': f.replace('\\', '/'),
            'ep_id': os.path.basename(os.path.dirname(f)),
            'name': os.path.basename(f),
            'res': f"{v.get('width')}x{v.get('height')}",
            'v_codec': v.get('codec_name'),
            'fps': v.get('r_frame_rate'),
            'v_dur': round(vd, 3),
            'black_segments': black_cnt,
            'a_codec': a.get('codec_name'),
            'a_dur': round(ad, 3),
            'channels': a.get('channels'),
            'sr_hz': a.get('sample_rate'),
            'i_lufs': i_lufs,
            'lra_lu': lra,
            'true_peak_dbfs': tp,
            'drift_ms': round(drift, 1),
            'sync_healthy': drift < 250.0
        })

    with open('./storage/full_av_audit_report.json', 'w', encoding='utf-8') as out:
        json.dump(results, out, indent=2)

    print("Audit completed successfully. Results saved to ./storage/full_av_audit_report.json")
    for r in results:
        print(f"[{r['ep_id']} | {r['name']}] Res: {r['res']} | V_Dur: {r['v_dur']}s | A_Dur: {r['a_dur']}s | Drift: {r['drift_ms']}ms | LUFS: {r['i_lufs']} | LRA: {r['lra_lu']} | Black: {r['black_segments']}")

if __name__ == '__main__':
    inspect_all()
