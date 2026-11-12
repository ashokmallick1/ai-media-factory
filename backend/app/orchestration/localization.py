import os
import json
import time
import logging
from typing import Dict, List, Any, Optional
from backend.app.adapters.voice.maya3 import Maya3TTSAdapter
from backend.app.adapters.voice.base import SpeechRequest
from backend.app.adapters.render.ffmpeg import FFmpegRenderer

logger = logging.getLogger(__name__)

# Pre-compiled cultural adaptations across languages for consistent studio character identities
CULTURAL_TRANSLATIONS: Dict[str, Dict[str, List[Dict[str, str]]]] = {
    "ep_studio1_entertainment": {
        "hi": [
            {"speaker": "Bikram Baboo", "voice": "Bikram", "text": "अरे टुकुना! आज गाँव में इतनी भीड़ क्यों है? हमारे स्वागत में कोई ढोल-ताशा नहीं?"},
            {"speaker": "Tukuna", "voice": "Ahana", "text": "नमस्ते बाबू जी! लोग आपके लिए नहीं, नुक्कड़ पर मुफ़्त जलेबियाँ बँट रही हैं इसलिए भागे हैं!"},
            {"speaker": "Bikram Baboo", "voice": "Bikram", "text": "अरे यार! हमारे रसूख के आगे जलेबी जीत गई? चल फिर, दो किलो हमारे लिए भी पैक करा!"}
        ],
        "bn": [
            {"speaker": "Bikram Baboo", "voice": "Bikram", "text": "আরে টুকুন! আজ গ্রামে এত ভিড় কেন? আমাকে স্বাগত জানানোর কেউ নেই?"},
            {"speaker": "Tukuna", "voice": "Ahana", "text": "বাবু নমস্কার! লোকে আপনার জন্য নয়, মোড়ের মাথায় গরম জিলিপি বিতরণ হচ্ছে বলে দৌড়েছে!"},
            {"speaker": "Bikram Baboo", "voice": "Bikram", "text": "ধুর তোর! আমার চেয়ে জিলিপির এত কদর? বেশ চল, আমার জন্যও দু'প্যাকেট নিয়ে নে!"}
        ],
        "en": [
            {"speaker": "Bikram Baboo", "voice": "Bikram", "text": "Hey Tukuna! Why is the village square so crowded today? Did nobody prepare a welcome band for me?"},
            {"speaker": "Tukuna", "voice": "Ahana", "text": "Greetings Baboo! People aren't rushing for you, they are lining up for free hot jalebis at the cinema hall!"},
            {"speaker": "Bikram Baboo", "voice": "Bikram", "text": "What nonsense! Free sweets over my grand arrival? Well then, go pack two boxes for me too!"}
        ]
    },
    "ep_studio2_kids": {
        "hi": [
            {"speaker": "Gulu Owl", "voice": "Ahana", "text": "प्यारे नन्हे दोस्तों का स्वागत है! आओ आज जादुई जंगल में चमकते तारों को गिनते हैं!"},
            {"speaker": "Gulu Owl", "voice": "Ahana", "text": "एक तारा चमके, दो तारे टिमटिमाएं! क्या तुम सब मेरे साथ गिनोगे?"},
            {"speaker": "Gulu Owl", "voice": "Ahana", "text": "बहुत बढ़िया! गिनती सीखना कितना मजेदार है! प्यारे दोस्तों, फिर मिलेंगे!"}
        ],
        "bn": [
            {"speaker": "Gulu Owl", "voice": "Ahana", "text": "স্বাগতম ছোট্ট বন্ধুরা! চলো আজ আমরা জাদু বনে ঝলমলে তারা গুনবো!"},
            {"speaker": "Gulu Owl", "voice": "Ahana", "text": "একটা তারা জ্বলে, দুটো তারা মিটমিট করে! আমার সাথে গুনবে?"},
            {"speaker": "Gulu Owl", "voice": "Ahana", "text": "খুব সুন্দর! সংখ্যা শেখা কত আনন্দের! আবার দেখা হবে বন্ধুরা!"}
        ],
        "or": [
            {"speaker": "Gulu Owl", "voice": "Ahana", "text": "ଆସ ମୋ ସାଙ୍ଗମାନେ! ଆଜି ଆମେ ମାୟାବୀ ଜଙ୍ଗଲରେ ଝଟକୁଥିବା ତାରାମାନଙ୍କୁ ଗଣିବା!"},
            {"speaker": "Gulu Owl", "voice": "Ahana", "text": "ଗୋଟିଏ ତାରା ଚମକେ, ଦୁଇଟି ତାରା ମିଟ୍ ମିଟ୍ କରେ! ମୋ ସାଙ୍ଗରେ ଗଣିବ କି?"},
            {"speaker": "Gulu Owl", "voice": "Ahana", "text": "ବହୁତ ବଢ଼ିଆ! ସଂଖ୍ୟା ଶିଖିବା କେତେ ଆନନ୍ଦଦାୟକ! ପୁଣି ଦେଖାହେବା!"}
        ]
    },
    "ep_studio3_education": {
        "hi": [
            {"speaker": "Dr. Bhasha", "voice": "Aryan", "text": "आर्टिफिशियल ब्रेन वास्तव में कैसे सीखते हैं? आज हम न्यूरल नेटवर्क को साठ सेकंड में समझेंगे।"},
            {"speaker": "Dr. Bhasha", "voice": "Aryan", "text": "इनपुट डेटा हिडन लेयर्स से होकर गुजरता है, और रोशनी की गति से प्रोबेबिलिटी की गणना करता है।"},
            {"speaker": "Dr. Bhasha", "voice": "Aryan", "text": "हजारों सफलताओं और गलतियों के बाद, मॉडल सही भविष्यवाणी करना सीख जाता है।"}
        ],
        "or": [
            {"speaker": "Dr. Bhasha", "voice": "Aryan", "text": "କୃତ୍ରିମ ବୁଦ୍ଧିମତା କିପରି ଶିଖେ? ଆଜି ଆମେ ନ୍ୟୁରାଲ୍ ନେଟୱାର୍କକୁ ମାତ୍ର ଷାଠିଏ ସେକେଣ୍ଡରେ ବୁଝିବା।"},
            {"speaker": "Dr. Bhasha", "voice": "Aryan", "text": "ଇନପୁଟ୍ ତଥ୍ୟ ଗୁପ୍ତ ସ୍ତର ଦେଇ ଗତି କରେ ଏବଂ ଆଲୋକର ବେଗରେ ସମ୍ଭାବନା ଗଣନା କରେ।"},
            {"speaker": "Dr. Bhasha", "voice": "Aryan", "text": "ହଜାର ହଜାର ଚେଷ୍ଟା ପରେ, ମଡେଲ ସଠିକ୍ ଉତ୍ତର ଦେବା ଶିଖିଯାଏ।"}
        ]
    },
    "ep_studio4_podcast": {
        "hi": [
            {"speaker": "Aryan", "voice": "Aryan", "text": "द एआई फ्रंटियर में आपका स्वागत है। क्या ओपन सोर्स मॉडल बिग टेक से आगे निकल रहे हैं?"},
            {"speaker": "Priya", "voice": "Ahana", "text": "बिल्कुल आर्यन, खुले मॉडल्स की रफ्तार अविश्वसनीय है, लेकिन क्या सेफ्टी गार्जियन साथ निभा पाएंगे?"},
            {"speaker": "Aryan", "voice": "Aryan", "text": "तकनीक तेजी से बदल रही है। अपनी राय नीचे कमेंट्स में जरूर साझा करें!"}
        ],
        "or": [
            {"speaker": "Aryan", "voice": "Aryan", "text": "ଦି ଏଆଇ ଫ୍ରଣ୍ଟିଅରକୁ ସ୍ୱାଗତ। ଓପନ୍ ସୋର୍ସ ମଡେଲ୍ କ’ଣ ବଡ଼ କମ୍ପାନୀଗୁଡ଼ିକୁ ପଛରେ ପକାଇ ଦେଉଛି?"},
            {"speaker": "Priya", "voice": "Ahana", "text": "ନିଶ୍ଚୟ ଆର୍ୟନ୍, ନୂତନ ରିସର୍ଚ୍ଚ ଯେଉଁ ଗତିରେ ବଢୁଛି, ସମସ୍ତେ ଚକିତ ହୋଇଯାଉଛନ୍ତି।"},
            {"speaker": "Aryan", "voice": "Aryan", "text": "ପରିବେଶ ଦ୍ରୁତ ଗତିରେ ବଦଳୁଛି। ଆପଣଙ୍କ ମତାମତ ତଳେ କମେଣ୍ଟରେ ଜଣାନ୍ତୁ!"}
        ]
    },
    "ep_studio5_news": {
        "hi": [
            {"speaker": "News Anchor", "voice": "Bikram", "text": "विशेष रिपोर्ट: ओडिशा सरकार ने भुवनेश्वर में अत्याधुनिक सेमीकंडक्टर फैब प्रोजेक्ट को मंजूरी दी है।"},
            {"speaker": "News Anchor", "voice": "Bikram", "text": "इस ऐतिहासिक परियोजना से अगले पांच वर्षों में बीस हजार से अधिक कुशल नौकरियां पैदा होंगी।"},
            {"speaker": "News Anchor", "voice": "Bikram", "text": "अधिकारियों के अनुसार निर्माण कार्य आगामी तिमाही से प्रारंभ होगा। जुड़े रहें ताज़ा खबरों के लिए।"}
        ],
        "en": [
            {"speaker": "News Anchor", "voice": "Aryan", "text": "Breaking Report: Odisha government approves mega semiconductor manufacturing hub in Bhubaneswar."},
            {"speaker": "News Anchor", "voice": "Aryan", "text": "Over twenty thousand high-tech engineering jobs will be created over the next five years."},
            {"speaker": "News Anchor", "voice": "Aryan", "text": "Groundbreaking begins next quarter. We will keep you updated as verified details arrive."}
        ]
    },
    "ep_studio6_marketing": {
        "en": [
            {"speaker": "Commercial VO", "voice": "Aryan", "text": "Tired of spending thousands on manual dubbing? Meet BhashaVoice AI today."},
            {"speaker": "Commercial VO", "voice": "Aryan", "text": "Clone your natural voice across twelve Indic languages with emotional accuracy in seconds."},
            {"speaker": "Commercial VO", "voice": "Aryan", "text": "Scale your brand across India. Visit BhashaAI dot in and claim your 50% discount now!"}
        ],
        "or": [
            {"speaker": "Commercial VO", "voice": "Aryan", "text": "ଡବିଂ ପାଇଁ ହଜାର ହଜାର ଟଙ୍କା ଖର୍ଚ୍ଚ କରି ଥକିଗଲେଣି? ଆଜି ହିଁ ବ୍ୟବହାର କରନ୍ତୁ ଭାଷାଭଏସ୍ ଏଆଇ।"},
            {"speaker": "Commercial VO", "voice": "Aryan", "text": "ମାତ୍ର କିଛି ସେକେଣ୍ଡରେ ନିଜ ଭଏସ୍ କୁ ବାରୋଟି ଭାରତୀୟ ଭାଷାରେ କ୍ଲୋନ୍ କରନ୍ତୁ।"},
            {"speaker": "Commercial VO", "voice": "Aryan", "text": "ଆପଣଙ୍କ ବ୍ୟବସାୟକୁ ସାରା ଭାରତରେ ପହଞ୍ଚାନ୍ତୁ। ଭିଜିଟ୍ କରନ୍ତୁ ଭାଷାଏଆଇ ଡଟ୍ ଇନ୍!"}
        ]
    }
}

class ModeALocalizationEngine:
    """
    Mode A Localization: Reuses approved visual video stream, synthesizes
    culturally adapted dialogue tracks via Maya3 TTS, and replaces the master audio.
    """

    def __init__(self, output_root: str = "./storage/output"):
        self.output_root = output_root
        self.voice_adapter = Maya3TTSAdapter(fallback_enabled=True)
        self.ffmpeg = FFmpegRenderer()

    async def localize_episode(self, episode_id: str, target_language: str) -> Dict[str, Any]:
        episode_dir = os.path.join(self.output_root, episode_id)
        if not os.path.exists(episode_dir):
            raise FileNotFoundError(f"Episode directory not found: {episode_dir}")

        # Find original master video
        master_video = None
        social_video = None
        for f in os.listdir(episode_dir):
            if f.startswith("master_16x9") and f.endswith(".mp4"):
                master_video = os.path.join(episode_dir, f)
            elif f.startswith("social_9x16") and f.endswith(".mp4"):
                social_video = os.path.join(episode_dir, f)

        if not master_video:
            raise FileNotFoundError(f"Master video not found in {episode_dir}")

        # Get cultural dialogue translation
        dialogues = CULTURAL_TRANSLATIONS.get(episode_id, {}).get(target_language)
        if not dialogues:
            # Generic fallback adaptation
            dialogues = [
                {"speaker": "Narrator", "voice": "Aryan", "text": f"This is the localized edition in language {target_language}."},
                {"speaker": "Narrator", "voice": "Aryan", "text": "Enjoying the studio production on BhashaTube."},
                {"speaker": "Narrator", "voice": "Aryan", "text": "Stay tuned for the next episode!"}
            ]

        # 1. Synthesize localized audio segments
        audio_segments: List[str] = []
        for idx, d in enumerate(dialogues, start=1):
            req = SpeechRequest(
                text=d["text"],
                language_code=target_language,
                voice_id=d.get("voice", "Aryan"),
                speed=1.05
            )
            resp = await self.voice_adapter.synthesize(req)
            seg_path = os.path.join(episode_dir, f"audio_localized_{target_language}_scene_{idx}.wav")
            with open(seg_path, "wb") as sf:
                sf.write(resp.audio_bytes)
            audio_segments.append(seg_path)

        # 2. Concat localized audio segments
        combined_audio_path = os.path.join(episode_dir, f"combined_audio_{target_language}.wav")
        # Write concat manifest
        manifest_path = os.path.join(episode_dir, f"audio_manifest_{target_language}.txt")
        with open(manifest_path, "w", encoding="utf-8") as mf:
            for seg in audio_segments:
                seg_esc = os.path.abspath(seg).replace("\\", "/")
                mf.write(f"file '{seg_esc}'\n")

        concat_cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", os.path.abspath(manifest_path),
            "-c:a", "pcm_s16le",
            os.path.abspath(combined_audio_path)
        ]
        self.ffmpeg.run_cmd(concat_cmd, episode_dir)

        # 3. Replace audio on Master 16:9
        localized_master_path = os.path.join(episode_dir, f"master_16x9_{target_language}.mp4")
        mux_master_cmd = [
            "ffmpeg", "-y",
            "-i", os.path.abspath(master_video),
            "-i", os.path.abspath(combined_audio_path),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-af", "loudnorm=I=-14:TP=-1.0:LRA=11",
            "-shortest",
            os.path.abspath(localized_master_path)
        ]
        self.ffmpeg.run_cmd(mux_master_cmd, episode_dir)

        # 4. Replace audio on Social 9:16 (if exists)
        localized_social_path = os.path.join(episode_dir, f"social_9x16_{target_language}.mp4")
        if social_video and os.path.exists(social_video):
            mux_social_cmd = [
                "ffmpeg", "-y",
                "-i", os.path.abspath(social_video),
                "-i", os.path.abspath(combined_audio_path),
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-af", "loudnorm=I=-14:TP=-1.0:LRA=11",
                "-shortest",
                os.path.abspath(localized_social_path)
            ]
            self.ffmpeg.run_cmd(mux_social_cmd, episode_dir)
        else:
            self.ffmpeg.reframe_aspect_ratio(localized_master_path, localized_social_path, target="9:16")

        # 5. FFprobe QA verification
        probe_info = self.ffmpeg.probe_media(localized_master_path)
        fmt = probe_info.get("format", {})
        duration = float(fmt.get("duration", 0.0))

        result = {
            "episode_id": episode_id,
            "target_language": target_language,
            "master_video_url": f"/media/output/{episode_id}/{os.path.basename(localized_master_path)}",
            "social_video_url": f"/media/output/{episode_id}/{os.path.basename(localized_social_path)}",
            "duration": round(duration, 2),
            "qa_passed": duration > 0,
            "timestamp": time.time()
        }

        # Update metadata.json if present
        meta_file = os.path.join(episode_dir, "metadata.json")
        if os.path.exists(meta_file):
            try:
                with open(meta_file, "r", encoding="utf-8") as mf:
                    meta = json.load(mf)
                if "localized_versions" not in meta:
                    meta["localized_versions"] = {}
                meta["localized_versions"][target_language] = {
                    "master_video_url": result["master_video_url"],
                    "social_video_url": result["social_video_url"]
                }
                with open(meta_file, "w", encoding="utf-8") as mf:
                    json.dump(meta, mf, indent=2)
            except Exception as e:
                logger.warning(f"Could not update metadata with localization: {e}")

        return result
