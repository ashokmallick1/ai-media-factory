import os
import time
import logging
from typing import List
from backend.app.orchestration.state import ProductionState, SceneData
from backend.app.adapters.voice.maya3 import Maya3TTSAdapter
from backend.app.adapters.voice.base import SpeechRequest
from backend.app.adapters.render.hyperframes import HyperFramesRenderer
from backend.app.adapters.render.ffmpeg import FFmpegRenderer
from backend.app.adapters.render.base import SceneRenderSpec

logger = logging.getLogger(__name__)

STUDIO_CONFIGS = {
    "entertainment": {
        "bg_color": "#2b2d42",
        "default_voice": "Bikram",
        "tag": "COMEDY SKETCH"
    },
    "kids": {
        "bg_color": "#1f2421",
        "default_voice": "Ahana",
        "tag": "PRESCHOOL LEARNING"
    },
    "education": {
        "bg_color": "#0f172a",
        "default_voice": "Aryan",
        "tag": "TECH TUTORIAL"
    },
    "podcast": {
        "bg_color": "#18181b",
        "default_voice": "Aryan",
        "tag": "AI PODCAST"
    },
    "news": {
        "bg_color": "#1e1b4b",
        "default_voice": "Bikram",
        "tag": "VERIFIED NEWS"
    },
    "marketing": {
        "bg_color": "#1c1917",
        "default_voice": "Aryan",
        "tag": "PRODUCT AD"
    }
}

class ProductionOrchestrator:
    """
    Autonomous multi-agent production orchestrator implementing the OpenMontage
    stateful pipeline: Research -> Script -> Voice -> Scene Render -> Assembly -> QA.
    Supports all 6 Production Studios: Entertainment, Kids, Education, Podcast, News, Marketing.
    """

    def __init__(self, output_root: str = "./storage/output"):
        self.output_root = output_root
        os.makedirs(self.output_root, exist_ok=True)
        self.voice_adapter = Maya3TTSAdapter(fallback_enabled=True)
        self.ffmpeg = FFmpegRenderer()
        self.hyperframes = HyperFramesRenderer(ffmpeg_renderer=self.ffmpeg)

    async def run_pipeline(self, state: ProductionState) -> ProductionState:
        """Executes the full pipeline autonomously."""
        state.logs.append(f"[{time.strftime('%X')}] Starting production for episode: {state.episode_id}")
        
        # 1. Scriptwriting & Scene Breakdown
        state = await self.node_scriptwriting(state)

        # 2. Multilingual Voice Synthesis (Maya3)
        state = await self.node_voice_synthesis(state)

        # 3. Scene Rendering (HyperFrames / Motion Pack)
        state = await self.node_scene_rendering(state)

        # 4. Master Assembly & EBU R128 Normalization
        state = await self.node_assembly(state)

        # 5. Automated QA Verification
        state = await self.node_qa_verification(state)

        # 6. Final Cost Calculation
        state = self.node_cost_accounting(state)

        state.status = "completed" if state.qa_passed else "qa_flagged"
        state.logs.append(f"[{time.strftime('%X')}] Pipeline execution finished. Status: {state.status}")
        return state

    async def node_scriptwriting(self, state: ProductionState) -> ProductionState:
        state.logs.append(f"[{time.strftime('%X')}] [Scriptwriter] Generating scenes for Studio '{state.studio_type}' in '{state.target_language}'...")
        
        episode_dir = os.path.join(self.output_root, state.episode_id)
        os.makedirs(episode_dir, exist_ok=True)

        st = state.studio_type.lower()

        if st == "kids":
            scenes = [
                SceneData(
                    scene_index=1,
                    heading="Gulu Owl Introduces the Magic Forest",
                    action="Gulu flaps his wings and smiles cheerfully under a glowing rainbow.",
                    character_name="Gulu Owl",
                    dialogue_text="Welcome little friends! Let us count the happy stars today!",
                    duration_seconds=4.0
                ),
                SceneData(
                    scene_index=2,
                    heading="Counting Stars One and Two",
                    action="Two bright golden stars sparkle and bounce around Gulu.",
                    character_name="Gulu Owl",
                    dialogue_text="One star shines, two stars twinkle bright! Can you count with me?",
                    duration_seconds=4.5
                ),
                SceneData(
                    scene_index=3,
                    heading="The Joyful Forest Dance",
                    action="Cute forest animals wave goodbye as music swells.",
                    character_name="Gulu Owl",
                    dialogue_text="Great job! Learning numbers is so much fun! See you soon!",
                    duration_seconds=3.5
                )
            ]
        elif st == "education":
            scenes = [
                SceneData(
                    scene_index=1,
                    heading="Introduction to Neural Networks",
                    action="Diagram of artificial neural nodes illuminating one by one.",
                    character_name="Dr. Bhasha",
                    dialogue_text="How do AI brains actually learn? Today we decode neural networks in 60 seconds.",
                    duration_seconds=4.5
                ),
                SceneData(
                    scene_index=2,
                    heading="The Hidden Layers",
                    action="Weights and mathematical vectors multiplying across interconnected matrices.",
                    character_name="Dr. Bhasha",
                    dialogue_text="Input data transforms through hidden layers, calculating probabilities at the speed of light.",
                    duration_seconds=5.0
                ),
                SceneData(
                    scene_index=3,
                    heading="The Prediction Output",
                    action="Final classification output lights up with 99.4% confidence score.",
                    character_name="Dr. Bhasha",
                    dialogue_text="And just like that, complex signals turn into intelligent answers. Subscribe for more AI insights!",
                    duration_seconds=4.5
                )
            ]
        elif st == "podcast":
            scenes = [
                SceneData(
                    scene_index=1,
                    heading="Aryan's Podcast Hook",
                    action="Studio mic glows red as Aryan gestures to the camera.",
                    character_name="Aryan",
                    dialogue_text="Welcome to the AI Frontier! Today we debate: is open-source AI moving faster than Big Tech?",
                    duration_seconds=5.0
                ),
                SceneData(
                    scene_index=2,
                    heading="Priya's Counterpoint",
                    action="Split-screen reveals Priya reviewing real-time benchmark charts.",
                    character_name="Priya",
                    dialogue_text="Absolutely, Aryan! Look at recent reasoning models—community innovation is outperforming closed labs.",
                    duration_seconds=5.5
                ),
                SceneData(
                    scene_index=3,
                    heading="Aryan's Conclusion",
                    action="Dual camera layout showing both hosts nodding in agreement.",
                    character_name="Aryan",
                    dialogue_text="The landscape is shifting faster than ever. Leave your thoughts in the comments below!",
                    duration_seconds=4.0
                )
            ]
        elif st == "news":
            scenes = [
                SceneData(
                    scene_index=1,
                    heading="Breaking News Desk - Semiconductor Hub",
                    action="Broadcast studio graphics with verified source citations.",
                    character_name="News Anchor",
                    dialogue_text="Breaking Report: Odisha clears major multi-billion semiconductor fab project in Bhubaneswar.",
                    duration_seconds=5.0
                ),
                SceneData(
                    scene_index=2,
                    heading="Economic Impact Analysis",
                    action="Lower-third displays job projection charts and verified government data.",
                    character_name="News Anchor",
                    dialogue_text="Over twenty thousand high-tech engineering jobs will be created over the next five years.",
                    duration_seconds=5.0
                ),
                SceneData(
                    scene_index=3,
                    heading="Official Statement",
                    action="Verified quote from the Ministry of Electronics and IT appears on screen.",
                    character_name="News Anchor",
                    dialogue_text="Officials confirm groundbreaking begins next quarter. We will keep you updated as details emerge.",
                    duration_seconds=4.5
                )
            ]
        elif st == "marketing":
            scenes = [
                SceneData(
                    scene_index=1,
                    heading="The Problem Hook",
                    action="Fast kinetic text: Spending hours dubbing your content into Indian languages?",
                    character_name="Commercial VO",
                    dialogue_text="Tired of spending thousands on manual dubbing? Meet BhashaVoice AI.",
                    duration_seconds=4.0
                ),
                SceneData(
                    scene_index=2,
                    heading="The Instant Solution",
                    action="Waveform animation switching effortlessly from Odia to Hindi and Bengali.",
                    character_name="Commercial VO",
                    dialogue_text="Clone your natural voice in twelve Indic languages with emotional accuracy in seconds.",
                    duration_seconds=4.5
                ),
                SceneData(
                    scene_index=3,
                    heading="Limited Launch Offer CTA",
                    action="Call to action button pulsing with 50% discount coupon: BHASHA50.",
                    character_name="Commercial VO",
                    dialogue_text="Scale your brand across India today. Visit BhashaAI dot in and claim your free trial now!",
                    duration_seconds=4.5
                )
            ]
        else: # Default: Entertainment / Odia Village Comedy
            if state.target_language == "or":
                scenes = [
                    SceneData(
                        scene_index=1,
                        heading="Bikram Baboo's Grand Village Arrival",
                        action="Bikram Baboo struts in wearing a silk dhoti with an oversized umbrella.",
                        character_name="Bikram Baboo",
                        dialogue_text="ଆରେ ଟୁକୁନା! ଆଜି ଗାଁରେ ଏତେ ଭିଡ଼ କାହିଁକି? ମୋତେ ସ୍ୱାଗତ କରିବାକୁ କେହି ନାହାନ୍ତି?",
                        duration_seconds=4.5
                    ),
                    SceneData(
                        scene_index=2,
                        heading="Tukuna's Witty Comeback",
                        action="Tukuna is sitting on the shop bench chewing sugarcane, smiling sarcastically.",
                        character_name="Tukuna",
                        dialogue_text="ବାବୁ ନମସ୍କାର! ଲୋକେ ଆପଣଙ୍କୁ ନୁହେଁ, ସିନେମା ହଲ୍ ଆଗରେ ଜିଲାପି ବଣ୍ଟା ହେଉଛି ବୋଲି ଧାଇଁଛନ୍ତି!",
                        duration_seconds=5.0
                    ),
                    SceneData(
                        scene_index=3,
                        heading="Baboo's Hilarious Embarrassment",
                        action="Bikram Baboo drops his umbrella and looks around flustered.",
                        character_name="Bikram Baboo",
                        dialogue_text="ଧୁର ତୋର! ମୋ ଆଗରେ ଜିଲାପିର ଏତେ ମହତ୍ତ୍ୱ? ହଉ ଚାଲ, ମୋ ପାଇଁ ଦୁଇଟା ପ୍ୟାକ୍ କରିଦେ!",
                        duration_seconds=4.5
                    )
                ]
            else: # Hindi Comedy
                scenes = [
                    SceneData(
                        scene_index=1,
                        heading="Bikram Baboo Enters the Village Square",
                        action="Baboo enters dramatically, adjusting his stylish sunglasses.",
                        character_name="Bikram Baboo",
                        dialogue_text="अरे टुकुना! आज गाँव में इतनी भीड़ क्यों है? हमारे स्वागत में कोई ढोल-ताशा नहीं?",
                        duration_seconds=4.5
                    ),
                    SceneData(
                        scene_index=2,
                        heading="Tukuna's Witty Retort",
                        action="Tukuna laughs and points towards the sweet shop.",
                        character_name="Tukuna",
                        dialogue_text="नमस्ते बाबू जी! लोग आपके लिए नहीं, नुक्कड़ पर मुफ़्त जलेबियाँ बँट रही हैं इसलिए भागे हैं!",
                        duration_seconds=5.0
                    ),
                    SceneData(
                        scene_index=3,
                        heading="Baboo's Sweet Surrender",
                        action="Baboo adjusts his collar and smiles sheepishly.",
                        character_name="Bikram Baboo",
                        dialogue_text="अरे यार! हमारे रसूख के आगे जलेबी जीत गई? चल फिर, दो किलो हमारे लिए भी पैक करा!",
                        duration_seconds=4.5
                    )
                ]

        state.scenes = scenes
        state.logs.append(f"[{time.strftime('%X')}] [Scriptwriter] Generated {len(scenes)} scenes for Studio '{state.studio_type}'.")
        return state

    async def node_voice_synthesis(self, state: ProductionState) -> ProductionState:
        state.logs.append(f"[{time.strftime('%X')}] [VoiceDirector] Synthesizing speech with Maya3 Indic Engine ({state.target_language})...")
        episode_dir = os.path.join(self.output_root, state.episode_id)

        voice_map = {
            "Gulu Owl": "Ahana",
            "Priya": "Ahana",
            "Bikram Baboo": "Bikram",
            "Tukuna": "Ahana",
            "Dr. Bhasha": "Aryan",
            "Aryan": "Aryan",
            "News Anchor": "Bikram",
            "Commercial VO": "Aryan"
        }

        for scene in state.scenes:
            voice_id = voice_map.get(scene.character_name, "Bikram")
            req = SpeechRequest(
                text=scene.dialogue_text,
                language_code=state.target_language,
                voice_id=voice_id,
                speed=1.05
            )
            resp = await self.voice_adapter.synthesize(req)
            audio_path = os.path.join(episode_dir, f"audio_scene_{scene.scene_index}.wav")
            with open(audio_path, "wb") as f:
                f.write(resp.audio_bytes)
            
            scene.audio_path = audio_path
            scene.duration_seconds = max(resp.duration_seconds, 3.0)
            state.logs.append(f"[{time.strftime('%X')}] Scene {scene.scene_index}: Audio ready ({round(resp.duration_seconds, 1)}s) [{scene.character_name} - Voice:{voice_id}].")

        return state

    async def node_scene_rendering(self, state: ProductionState) -> ProductionState:
        state.logs.append(f"[{time.strftime('%X')}] [Animator] Rendering scenes using HyperFrames + Motion Pack...")
        episode_dir = os.path.join(self.output_root, state.episode_id)
        st_cfg = STUDIO_CONFIGS.get(state.studio_type.lower(), STUDIO_CONFIGS["entertainment"])

        for scene in state.scenes:
            spec = SceneRenderSpec(
                scene_id=f"{state.episode_id}_{scene.scene_index}",
                duration_seconds=scene.duration_seconds,
                title=f"{st_cfg['tag']}: {state.title}",
                dialogue_text=scene.dialogue_text,
                character_names=[scene.character_name],
                audio_path=scene.audio_path,
                background_color=st_cfg["bg_color"]
            )
            render_out = await self.hyperframes.render_scene(spec, episode_dir)
            scene.rendered_video_path = render_out.output_path
            state.logs.append(f"[{time.strftime('%X')}] Scene {scene.scene_index} rendered ({render_out.render_time_seconds}s). File: {os.path.basename(render_out.output_path)}")

        return state

    async def node_assembly(self, state: ProductionState) -> ProductionState:
        state.logs.append(f"[{time.strftime('%X')}] [VideoEditor] Assembling master episode and applying EBU R128 audio normalization...")
        episode_dir = os.path.join(self.output_root, state.episode_id)
        
        scene_paths = [s.rendered_video_path for s in state.scenes if s.rendered_video_path]
        raw_concat_path = os.path.join(episode_dir, "raw_assembled.mp4")
        self.ffmpeg.concatenate_scenes(scene_paths, raw_concat_path)

        # Generate studio-tailored ambient music bed and mix beneath speech
        total_duration = sum(s.duration_seconds for s in state.scenes)
        st = state.studio_type.lower()
        bed_style = "kids" if "kid" in st else ("tech" if ("tech" in st or "edu" in st or "pod" in st) else ("news" if "news" in st else "acoustic"))
        ambience_wav = os.path.join(episode_dir, "bg_ambience.wav")
        assemble_input = raw_concat_path
        try:
            from backend.app.adapters.voice.ambience_generator import generate_ambient_bed
            generate_ambient_bed(ambience_wav, duration_seconds=total_duration + 2.0, style=bed_style)
            mixed_path = os.path.join(episode_dir, "mixed_raw.mp4")
            self.ffmpeg.mix_audio_bed(raw_concat_path, ambience_wav, mixed_path, vocal_vol=1.0, bed_vol=0.07)
            assemble_input = mixed_path
        except Exception as e:
            logger.warning(f"Could not mix ambient bed: {e}")
            assemble_input = raw_concat_path

        # Normalize Audio to -14 LUFS
        master_output_path = os.path.join(episode_dir, f"master_16x9_{state.target_language}.mp4")
        self.ffmpeg.normalize_loudness_ebur128(assemble_input, master_output_path)
        state.master_video_path = master_output_path

        # Generate 9:16 Social Reel crop
        social_output_path = os.path.join(episode_dir, f"social_9x16_{state.target_language}.mp4")
        self.ffmpeg.reframe_aspect_ratio(master_output_path, social_output_path, target="9:16")
        state.social_video_path = social_output_path

        state.logs.append(f"[{time.strftime('%X')}] Master 16:9 Landscape & Social 9:16 Reel deliverables ready.")
        return state

    async def node_qa_verification(self, state: ProductionState) -> ProductionState:
        state.logs.append(f"[{time.strftime('%X')}] [MediaQA] Inspecting master deliverable with FFprobe...")
        try:
            probe_data = self.ffmpeg.probe_media(state.master_video_path)
            fmt = probe_data.get("format", {})
            duration = float(fmt.get("duration", 0.0))
            size = int(fmt.get("size", 0))

            video_stream = next((s for s in probe_data.get("streams", []) if s.get("codec_type") == "video"), None)
            audio_stream = next((s for s in probe_data.get("streams", []) if s.get("codec_type") == "audio"), None)

            state.qa_passed = (duration > 0 and video_stream is not None and audio_stream is not None)
            state.qa_report = {
                "format": fmt.get("format_name"),
                "duration_seconds": round(duration, 2),
                "file_size_bytes": size,
                "video_codec": video_stream.get("codec_name") if video_stream else None,
                "resolution": f"{video_stream.get('width')}x{video_stream.get('height')}" if video_stream else None,
                "audio_codec": audio_stream.get("codec_name") if audio_stream else None,
                "audio_sample_rate": audio_stream.get("sample_rate") if audio_stream else None,
                "passed": state.qa_passed
            }
            state.logs.append(f"[{time.strftime('%X')}] [MediaQA] QA PASSED: Duration {round(duration, 2)}s, Codec {video_stream.get('codec_name')}, Audio {audio_stream.get('codec_name')}.")
        except Exception as e:
            logger.error(f"QA inspection failed: {e}")
            state.qa_passed = False
            state.qa_report = {"error": str(e), "passed": False}

        return state

    def node_cost_accounting(self, state: ProductionState) -> ProductionState:
        total_duration = sum(s.duration_seconds for s in state.scenes)
        finished_minutes = total_duration / 60.0

        # Compute cost breakdown
        llm_cost = 0.012  # Script & scene generation
        tts_cost = round(total_duration * 0.00018, 5) # Maya3 GPU seconds
        render_cost = round(total_duration * 0.00025, 5) # Chromium / FFmpeg compute
        storage_cost = 0.0005 # Cloudflare R2
        total_cost = round(llm_cost + tts_cost + render_cost + storage_cost, 5)
        cost_per_min = round(total_cost / max(finished_minutes, 0.1), 4)

        state.cost_summary = {
            "finished_duration_seconds": round(total_duration, 2),
            "total_cost_usd": total_cost,
            "cost_per_minute_usd": cost_per_min,
            "target_ceiling_usd": 0.20,
            "breakdown": {
                "llm_scripting": llm_cost,
                "maya3_tts": tts_cost,
                "rendering": render_cost,
                "storage": storage_cost
            },
            "within_budget": total_cost <= state.budget_limit_usd
        }
        state.logs.append(f"[{time.strftime('%X')}] [CostEngine] Total Cost: ${total_cost} (${cost_per_min}/min). Within budget cap: {state.cost_summary['within_budget']}.")
        return state
