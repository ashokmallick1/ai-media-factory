import os
import math
import struct
import wave

def generate_ambient_bed(output_wav_path: str, duration_seconds: float = 30.0, style: str = "acoustic") -> str:
    """
    Generates a soft, warm harmonic background ambience track
    (gentle chord pad with slow attack/decay, zero harsh harmonics or test tones)
    designed to sit at -24 to -28 dB underneath dialogue.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)
    sample_rate = 44100
    num_samples = int(sample_rate * duration_seconds)

    # Style chord frequencies (Hz) - gentle warm musical triads
    if style == "kids":
        # Playful G major pentatonic / music box
        freqs = [392.0, 493.88, 587.33, 783.99]
    elif style == "tech":
        # Ambient dreamy D minor 9th (cyber / futuristic)
        freqs = [146.83, 220.0, 261.63, 329.63]
    elif style == "news":
        # Serious broadcast low fifths
        freqs = [130.81, 196.0, 261.63]
    else: # "acoustic" / comedy / general
        # Warm C major 7th folk pad
        freqs = [130.81, 164.81, 196.0, 246.94]

    with wave.open(output_wav_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2) # 16-bit PCM
        wf.setframerate(sample_rate)

        # Generate audio samples
        chunk_size = 4096
        samples_written = 0

        while samples_written < num_samples:
            current_chunk = min(chunk_size, num_samples - samples_written)
            raw_bytes = bytearray()
            
            for i in range(current_chunk):
                t = (samples_written + i) / sample_rate
                # Slow gentle LFO volume breath (0.15 Hz = 6.6s cycle)
                lfo = 0.65 + 0.35 * math.sin(2 * math.pi * 0.15 * t)
                
                # Sum chords with soft harmonic roll-off
                val = 0.0
                for f_idx, f in enumerate(freqs):
                    # Subtle stereo chorusing / vibrato
                    mod_f = f + 0.3 * math.sin(2 * math.pi * 0.4 * t + f_idx)
                    val += math.sin(2 * math.pi * mod_f * t) / (f_idx + 1)
                
                # Fade in / fade out at edges
                fade = 1.0
                if t < 1.5:
                    fade = t / 1.5
                elif t > (duration_seconds - 1.5):
                    fade = max(0.0, (duration_seconds - t) / 1.5)

                # Keep peak level very soft (~ -24 dB relative to full scale)
                amplitude = 2500 # max 32767 -> ~ -22 dBFS
                sample = int(val * amplitude * lfo * fade * 0.35)
                sample = max(-32768, min(32767, sample))
                raw_bytes.extend(struct.pack("<h", sample))

            wf.writeframes(raw_bytes)
            samples_written += current_chunk

    return output_wav_path

if __name__ == "__main__":
    test_wav = "./storage/test_ambience.wav"
    generate_ambient_bed(test_wav, 10.0, "acoustic")
    print(f"Generated test ambient bed at {test_wav}")
