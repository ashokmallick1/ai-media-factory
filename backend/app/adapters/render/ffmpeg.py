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

    def _infer_studio(self, spec: SceneRenderSpec) -> str:
        t = (spec.title or "").lower()
        s_id = (spec.scene_id or "").lower()
        combined = f"{t} {s_id}"
        if "kid" in combined or "owl" in combined or "rhyme" in combined:
            return "kids"
        if "neural" in combined or "tutorial" in combined or "tech" in combined or "education" in combined:
            return "education"
        if "podcast" in combined or "frontier" in combined or "alex" in combined:
            return "podcast"
        if "news" in combined or "fab" in combined or "semiconductor" in combined or "report" in combined:
            return "news"
        if "marketing" in combined or "bhasha" in combined or "voice" in combined or "promo" in combined:
            return "marketing"
        return "entertainment"

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

        # Generate center visual spotlight card
        card_png_file = f"card_{spec.scene_id}.png"
        full_card_path = os.path.join(output_dir, card_png_file)
        has_card = False
        try:
            from backend.app.adapters.render.visual_card_generator import generate_scene_card
            st = self._infer_studio(spec)
            char = spec.character_names[0] if spec.character_names else (spec.title.split(":")[0] if ":" in spec.title else "Spotlight")
            generate_scene_card(full_card_path, character_name=char, studio_type=st, scene_heading=spec.title)
            if os.path.exists(full_card_path):
                has_card = True
        except Exception as e:
            logger.warning(f"Could not generate visual card for scene {spec.scene_id}: {e}")

        if has_card:
            filter_complex = (
                f"color=c={spec.background_color}:s={width}x{height}:d={dur}[bg];"
                f"[bg][1:v]overlay=(W-w)/2:(H-h)/2-40:shortest=1[with_card];"
                f"[0:a]showwaves=s=1100x70:mode=line:colors=0xfca311@0.85:scale=sqrt[wave];"
                f"[with_card][wave]overlay=(W-w)/2:{height-250}:shortest=1[with_wave];"
                f"[with_wave]drawbox=x=0:y={height-170}:w={width}:h=170:color=black@0.65:t=fill[box];"
                f"[box]drawtext={font_clause}textfile={title_txt_file}:fontsize=40:fontcolor=white:x=(w-text_w)/2:y=75[titled];"
                f"[titled]drawtext={font_clause}textfile={dialogue_txt_file}:fontsize=32:fontcolor=yellow:x=(w-text_w)/2:y={height-115}[outv]"
            )
        else:
            filter_complex = (
                f"color=c={spec.background_color}:s={width}x{height}:d={dur}[bg];"
                f"[0:a]showwaves=s=1100x70:mode=line:colors=0xfca311@0.85:scale=sqrt[wave];"
                f"[bg][wave]overlay=(W-w)/2:{height-250}:shortest=1[with_wave];"
                f"[with_wave]drawbox=x=0:y={height-170}:w={width}:h=170:color=black@0.65:t=fill[box];"
                f"[box]drawtext={font_clause}textfile={title_txt_file}:fontsize=40:fontcolor=white:x=(w-text_w)/2:y=75[titled];"
                f"[titled]drawtext={font_clause}textfile={dialogue_txt_file}:fontsize=32:fontcolor=yellow:x=(w-text_w)/2:y={height-115}[outv]"
            )

        cmd = [self.ffmpeg, "-y"]

        if spec.audio_path and os.path.exists(spec.audio_path):
            norm_audio = os.path.abspath(spec.audio_path).replace("\\", "/")
            cmd.extend(["-i", norm_audio])
        else:
            cmd.extend(["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"])

        if has_card:
            norm_card = os.path.abspath(full_card_path).replace("\\", "/")
            cmd.extend(["-loop", "1", "-i", norm_card])

        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-map", "0:a",
            "-shortest",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-profile:v", "high",
            "-level", "4.1",
            "-g", "30",
            "-keyint_min", "30",
            "-c:a", "aac",
            "-b:a", "192k",
            "-r", str(spec.fps),
            "-t", str(dur),
            "-movflags", "+faststart",
            out_filename
        ])

        try:
            subprocess.run(cmd, cwd=output_dir, capture_output=True, check=True)
        finally:
            for p in [full_title_path, full_dial_path, full_card_path]:
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
            "-profile:v", "high",
            "-level", "4.1",
            "-g", "30",
            "-keyint_min", "30",
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

    def mix_audio_bed(self, input_video: str, bed_wav: str, output_video: str, vocal_vol: float = 1.0, bed_vol: float = 0.08) -> str:
        """
        Mixes a soft background ambience bed under dialogue.
        """
        cmd = [
            self.ffmpeg, "-y",
            "-i", os.path.abspath(input_video),
            "-i", os.path.abspath(bed_wav),
            "-filter_complex", f"[0:a]volume={vocal_vol}[vocal];[1:a]volume={bed_vol}[bgm];[vocal][bgm]amix=inputs=2:duration=first:dropout_transition=2[outa]",
            "-map", "0:v",
            "-map", "[outa]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            os.path.abspath(output_video)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return output_video

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
            "-movflags", "+faststart",
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
            "-profile:v", "high",
            "-level", "4.1",
            "-g", "30",
            "-keyint_min", "30",
            "-c:a", "copy",
            "-movflags", "+faststart",
            os.path.abspath(output_video)
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        return output_video
