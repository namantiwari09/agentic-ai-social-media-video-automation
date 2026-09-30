import json
import os
import re
import subprocess
import requests
from pathlib import Path

BASE = Path(r"D:\agentic-social-media-ai")
AUDIO_DIR = BASE / "audio"
TEMP_DIR = BASE / "output" / "voice_temp"

AUDIO_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

TOPIC = "Artificial Intelligence and how it is changing the future"

print()
print("======================================")
print(" AI OFFLINE VOICEOVER GENERATOR")
print("======================================")
print()

# --------------------------------------------------
# 1. Generate narration using Ollama
# --------------------------------------------------

print("[1/3] Connecting to Ollama...")

prompt = f"""
You are a professional social media video narrator.

Create narration for a 30-second vertical video about:

{TOPIC}

Create exactly 5 short narration scenes.

Return ONLY valid JSON using this structure:

{{
  "scenes": [
    {{
      "scene_number": 1,
      "narration": "short narration"
    }},
    {{
      "scene_number": 2,
      "narration": "short narration"
    }},
    {{
      "scene_number": 3,
      "narration": "short narration"
    }},
    {{
      "scene_number": 4,
      "narration": "short narration"
    }},
    {{
      "scene_number": 5,
      "narration": "short call to action"
    }}
  ]
}}

Each narration should be short enough for approximately 5 to 7 seconds.
"""

try:
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    response.raise_for_status()
    result = response.json()["response"]

except Exception as e:
    print()
    print("ERROR CONNECTING TO OLLAMA")
    print(e)
    input("Press Enter to close...")
    raise SystemExit

print("[2/3] AI narration generated.")

result = result.replace("```json", "")
result = result.replace("```", "")
result = result.strip()

match = re.search(r"\{.*\}", result, re.DOTALL)

if not match:
    print("ERROR: Invalid AI response.")
    print(result)
    input("Press Enter to close...")
    raise SystemExit

try:
    data = json.loads(match.group())
except Exception as e:
    print("ERROR: Could not parse AI JSON.")
    print(e)
    print(result)
    input("Press Enter to close...")
    raise SystemExit

scenes = data.get("scenes", [])

if not scenes:
    print("ERROR: No narration scenes found.")
    input("Press Enter to close...")
    raise SystemExit

# --------------------------------------------------
# 2. Windows Offline Text-to-Speech
# --------------------------------------------------

powershell_script = TEMP_DIR / "tts.ps1"

powershell_code = r'''
param(
    [string]$TextFile,
    [string]$OutputFile
)

Add-Type -AssemblyName System.Speech

$text = Get-Content -Path $TextFile -Raw

$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer

$synth.Rate = 0
$synth.Volume = 100

$synth.SetOutputToWaveFile($OutputFile)

$synth.Speak($text)

$synth.SetOutputToNull()

$synth.Dispose()
'''

powershell_script.write_text(
    powershell_code,
    encoding="utf-8"
)

for scene in scenes:

    number = int(scene.get("scene_number", 1))
    narration = str(scene.get("narration", "")).strip()

    print(f"Generating offline voice for Scene {number}...")

    text_file = TEMP_DIR / f"scene_{number}.txt"
    wav_file = TEMP_DIR / f"scene_{number}.wav"
    mp3_file = AUDIO_DIR / f"scene_{number}.mp3"

    text_file.write_text(
        narration,
        encoding="utf-8"
    )

    # Generate WAV using Windows built-in speech engine
    command = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(powershell_script),
        "-TextFile",
        str(text_file),
        "-OutputFile",
        str(wav_file)
    ]

    process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if process.returncode != 0 or not wav_file.exists():
        print()
        print("======================================")
        print("VOICE GENERATION ERROR")
        print("======================================")
        print(process.stderr)
        print()
        input("Press Enter to close...")
        raise SystemExit

    # Convert WAV to MP3 using FFmpeg
    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-i",
        str(wav_file),
        "-codec:a",
        "libmp3lame",
        "-q:a",
        "4",
        str(mp3_file)
    ]

    process = subprocess.run(
        ffmpeg_command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    )

    if process.returncode != 0 or not mp3_file.exists():
        print()
        print("======================================")
        print("FFMPEG AUDIO ERROR")
        print("======================================")
        print(process.stderr)
        print()
        input("Press Enter to close...")
        raise SystemExit

print()
print("[3/3] VOICEOVER CREATED SUCCESSFULLY!")
print()

print("======================================")
print(" VOICEOVER FILES READY")
print("======================================")
print()

for scene in scenes:
    number = int(scene.get("scene_number", 1))
    print(f"Scene {number}: audio\\scene_{number}.mp3")

print()
print("Voice Engine: Windows System.Speech")
print("AI Model: Llama 3.2")
print("Audio Engine: FFmpeg")
print("Scenes:", len(scenes))
print()
print("======================================")
print()

input("Press Enter to close...")