---
name: media-qa-auditor
description: Automated media quality assurance, FFprobe inspection, audio loudness normalization (EBU R128), and render integrity verification.
---

# Media QA Auditor Skill

## Purpose
Enforces deterministic delivery standards for every generated video before final export or publishing.

## Verification Checklist
1. **Container & Stream Integrity:**
   - Command: `ffprobe -v error -show_entries format=duration,size,bit_rate -show_streams -of json <video_path>`
   - Verify zero frame corruption, duration match between video and audio streams (drift < 100ms).
2. **Audio Loudness (EBU R128):**
   - Target: Integrated loudness -14.0 LUFS (±1.0 LUFS) for YouTube/Social.
   - Max True Peak: -1.0 dBTP.
   - Normalization command:
     `ffmpeg -i input.mp4 -af loudnorm=I=-14:TP=-1.0:LRA=11 -c:v copy output_normalized.mp4`
3. **Black Frame Detection:**
   - Scan for blank renders:
     `ffmpeg -i input.mp4 -vf "blackdetect=d=0.5:pix_th=0.10" -an -f null -`
4. **Subtitles & Margin Safety:**
   - Verify subtitles render within the 80% inner boundary for mobile 9:16 and desktop 16:9 displays.
