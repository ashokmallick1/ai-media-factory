import os
import json
import time
import subprocess
import logging
from typing import List, Dict, Any, Optional
from backend.app.adapters.render.base import BaseRenderEngine, SceneRenderSpec, RenderOutput

logger = logging.getLogger(__name__)

class FFmpegRenderer(BaseRenderEngine):
    """
    FFmpeg media engine enforcing the 'probe -> edit -> check -> verify' contract.
    Handles scene synthesis, full episode assembly, audio normalization, and QA probing.
    """

    def __init__(self, ffmpeg_bin: str = "ffmpeg", ffprobe_bin: str = "ffprobe"):
        self.ffmpeg = ffmpeg_bin
        self.ffprobe = ffprobe_bin
        self.font_path = self._detect_font()

    def _detect_font(self) -> Optional[str]:
        # Detect Unicode/Indic font on Windows or Linux
        candidates = [
            "C:/Windows/Fonts/Nirmala.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/opentype/noto/NotoSans-Regular.ttf"
        ]
        for c in candidates:
            if os.path.exists(c):
                drive, rest = os.path.splitdrive(c)
                if drive:
                    return f"{drive[0]}\\:{rest.replace('\\', '/')}"
                return c.replace('\\', '/')
        return None

    def run_cmd(self, cmd: List[str], cwd: Optional[str] = None) -> subprocess.CompletedProcess:
        """Executes an FFmpeg command with proper error handling."""
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)

    def probe_media(self, file_path: str) -> Dict[str, Any]:
        """Inspect file streams, codec, duration, and metadata via ffprobe."""
        cmd = [
            self.ffprobe,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            os.path.abspath(file_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)

    async def render_scene(self, spec: SceneRenderSpec, output_dir: str) -> RenderOutput:
        """
        Synthesizes a visual scene MP4 with high-clarity canvas title, dialogue card,
        and audio track using local textfiles with cwd=output_dir.
        """
        os.makedirs(output_dir, exist_ok=True)
        out_filename = f"scene_{spec.scene_id}.mp4"
        out_file = os.path.join(output_dir, out_filename)
        start_time = time.time()

        width, height = spec.resolution
        dur = max(spec.duration_seconds, 1.0)
        
        # Write title and dialogue to local utf-8 text files in output_dir
        title_txt_file = f"title_{spec.scene_id}.txt"
        dialogue_txt_file = f"dial_{spec.scene_id}.txt"

        full_title_path = os.path.join(output_dir, title_txt_file)
        full_dial_path = os.path.join(output_dir, dialogue_txt_file)

        with open(full_title_path, "w", encoding="utf-8") as f:
            f.write(spec.title or "AI Media Factory")
        with open(full_dial_path, "w", encoding="utf-8") as f:
            f.write(spec.dialogue_text or "")

        font_clause = f"fontfile='{self.font_path}':" if self.font_path else ""

        filter_complex = (
            f"color=c={spec.background_color}:s={width}x{height}:d={dur}[bg];"
            f"[bg]drawbox=x=0:y={height-180}:w={width}:h=180:color=black@0.6:t=fill[box];"
            f"[box]drawtext={font_clause}textfile={title_txt_file}:fontsize=42:fontcolor=white:x=(w-text_w)/2:y=80[titled];"
            f"[titled]drawtext={font_clause}textfile={dialogue_txt_file}:fontsize=32:fontcolor=yellow:x=(w-text_w)/2:y={height-120}[outv]"
        )

        cmd = [self.ffmpeg, "-y"]

        if spec.audio_path and os.path.exists(spec.audio_path):
            norm_audio = os.path.abspath(spec.audio_path).replace("\\", "/")
            cmd.extend(["-i", norm_audio])
        else:
            cmd.extend(["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"])

        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-map", "0:a",
            "-shortest",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-r", str(spec.fps),
            "-t", str(dur),
            out_filename
        ])

        try:
            subprocess.run(cmd, cwd=output_dir, capture_output=True, check=True)
        finally:
            for p in [full_title_path, full_dial_path]:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception:
                        pass

        render_duration = round(time.time() - start_time, 2)
        file_size = os.path.getsize(out_file)

        return RenderOutput(
            scene_id=spec.scene_id,
            output_path=out_file,
            duration_seconds=dur,
            file_size_bytes=file_size,
            resolution=spec.resolution,
            render_time_seconds=render_duration
        )

    def concatenate_scenes(self, scene_video_paths: List[str], output_path: str) -> str:
        """Concatenates multiple scene MP4 files into a continuous master episode."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        concat_list_file = output_path + ".txt"

        with open(concat_list_file, "w", encoding="utf-8") as f:
            for path in scene_video_paths:
                norm_path = os.path.abspath(path).replace("\\", "/")
                f.write(f"file '{norm_path}'\n")

        cmd = [
            self.ffmpeg, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", os.path.abspath(concat_list_file),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            os.path.abspath(output_path)
        ]
        try:
            subprocess.run(cmd, capture_output=True, check=True)
        finally:
            if os.path.exists(concat_list_file):
                try:
                    os.remove(concat_list_file)
                except Exception:
                    pass
        return output_path

    def normalize_loudness_ebur128(self, input_video: str, output_video: str) -> str:
        """
        Applies EBU R128 loudness normalization (-14 LUFS target for YouTube / Social).
        """
        cmd = [
            self.ffmpeg, "-y",
            "-i", os.path.abspath(input_video),
            "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=11",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            os.path.abspath(output_video)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return output_video

    def reframe_aspect_ratio(self, input_video: str, output_video: str, target: str = "9:16") -> str:
        """
        Converts 16:9 master to 9:16 vertical reels with blurred pillarbox backdrop.
        """
        filter_str = (
            "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20:5[bg];"
            "[0:v]scale=1080:1920:force_original_aspect_ratio=decrease[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2[outv]"
        )
        cmd = [
            self.ffmpeg, "-y",
            "-i", os.path.abspath(input_video),
            "-filter_complex", filter_str,
            "-map", "[outv]",
            "-map", "0:a?",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-c:a", "copy",
            os.path.abspath(output_video)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return output_video
