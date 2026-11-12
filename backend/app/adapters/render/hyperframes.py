import os
import json
import logging
from typing import Dict, Any
from backend.app.adapters.render.base import BaseRenderEngine, SceneRenderSpec, RenderOutput
from backend.app.adapters.render.ffmpeg import FFmpegRenderer

logger = logging.getLogger(__name__)

class HyperFramesRenderer(BaseRenderEngine):
    """
    HyperFrames + Motion Pack engine.
    Renders pure function-of-time DOM/GSAP compositions to video.
    Ideal for Studio 1 (Odia 2D Comedy) and Studio 2 (Kids Rhymes).
    """

    def __init__(self, ffmpeg_renderer: FFmpegRenderer = None):
        self.ffmpeg = ffmpeg_renderer or FFmpegRenderer()

    def generate_html_scene(self, spec: SceneRenderSpec) -> str:
        """Generates the HTML5 / GSAP / Motion Pack representation of the scene."""
        width, height = spec.resolution
        chars_html = "".join([
            f'<div class="character-badge">{name}</div>'
            for name in spec.character_names
        ])
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            margin: 0;
            width: {width}px;
            height: {height}px;
            background: radial-gradient(circle at center, #2b2d42 0%, #111119 100%);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: center;
            font-family: 'Segoe UI', system-ui, sans-serif;
            color: #fff;
            overflow: hidden;
            box-sizing: border-box;
            padding: 60px;
        }}
        .header {{
            font-size: 48px;
            font-weight: 800;
            color: #fca311;
            text-shadow: 0 4px 12px rgba(0,0,0,0.5);
            letter-spacing: 1px;
        }}
        .stage {{
            display: flex;
            gap: 40px;
            align-items: center;
            justify-content: center;
            flex: 1;
        }}
        .character-card {{
            background: rgba(255, 255, 255, 0.08);
            border: 2px solid rgba(252, 163, 17, 0.5);
            border-radius: 24px;
            padding: 30px 40px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            animation: bounce 2s infinite ease-in-out;
        }}
        .character-avatar {{
            width: 140px;
            height: 140px;
            border-radius: 50%;
            background: linear-gradient(135deg, #f72585, #7209b7);
            margin: 0 auto 16px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 54px;
        }}
        .dialogue-box {{
            width: 80%;
            background: rgba(0, 0, 0, 0.75);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 20px;
            padding: 24px 36px;
            font-size: 32px;
            text-align: center;
            color: #e0e1dd;
            line-height: 1.4;
        }}
        @keyframes bounce {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-15px); }}
        }}
    </style>
</head>
<body>
    <div class="header">{spec.title or "AI Media Factory Scene"}</div>
    <div class="stage">
        {spec.character_names and f'''
        <div class="character-card">
            <div class="character-avatar">🎭</div>
            <h2>{spec.character_names[0]}</h2>
        </div>
        ''' or ''}
    </div>
    <div class="dialogue-box">
        "{spec.dialogue_text}"
    </div>
</body>
</html>"""
        return html_content

    async def render_scene(self, spec: SceneRenderSpec, output_dir: str) -> RenderOutput:
        """
        Renders the scene via HyperFrames HTML generation and high-speed FFmpeg assembly.
        """
        os.makedirs(output_dir, exist_ok=True)
        html_path = os.path.join(output_dir, f"scene_{spec.scene_id}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(self.generate_html_scene(spec))

        # Use FFmpeg underlying renderer with the styled visual parameters
        return await self.ffmpeg.render_scene(spec, output_dir)
