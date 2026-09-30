import json
import os
import re
import subprocess
import requests
from pathlib import Path

# ============================================================
# AI SOCIAL MEDIA VIDEO AUTOMATION
# ============================================================

BASE = Path(r"D:\agentic-social-media-ai")
VIDEO_DIR = BASE / "videos"
TEMP_DIR = BASE / "output" / "video_temp"

VIDEO_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

TOPIC = "Artificial Intelligence and how it is changing the future"

print()
print("======================================")
print(" AI SOCIAL MEDIA VIDEO AUTOMATION")
print("======================================")
print()

# ============================================================
# 1. CONNECT TO OLLAMA
# ============================================================

print("[1/4] Connecting to Ollama...")

prompt = f"""
You are an expert social media video creator.

Create a 30-second vertical social media video about:

{TOPIC}

Create exactly 5 scenes.

Return ONLY valid JSON.

Use this exact structure:

{{
  "title": "short video title",
  "scenes": [
    {{
      "scene_number": 1,
      "narration": "short narration for scene 1",
      "visual": "visual description for scene 1",
      "duration": 6
    }},
    {{
      "scene_number": 2,
      "narration": "short narration for scene 2",
      "visual": "visual description for scene 2",
      "duration": 6
    }},
    {{
      "scene_number": 3,
      "narration": "short narration for scene 3",
      "visual": "visual description for scene 3",
      "duration": 6
    }},
    {{
      "scene_number": 4,
      "narration": "short narration for scene 4",
      "visual": "visual description for scene 4",
      "duration": 6
    }},
    {{
      "scene_number": 5,
      "narration": "final call to action",
      "visual": "visual description for scene 5",
      "duration": 6
    }}
  ]
}}
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

    ollama_data = response.json()
    result = ollama_data["response"]

except Exception as e:
    print()
    print("ERROR: Could not connect to Ollama.")
    print(e)
    print()
    input("Press Enter to exit...")
    raise SystemExit


# ============================================================
# 2. PARSE AI RESPONSE
# ============================================================

print("[2/4] AI generated the content.")

result = result.replace("```json", "")
result = result.replace("```", "")
result = result.strip()

match = re.search(r"\{.*\}", result, re.DOTALL)

if not match:
    print()
    print("ERROR: AI did not return valid JSON.")
    print(result)
    print()
    input("Press Enter to exit...")
    raise SystemExit

try:
    data = json.loads(match.group())
except Exception as e:
    print()
    print("ERROR: Could not parse AI JSON.")
    print(e)
    print(result)
    print()
    input("Press Enter to exit...")
    raise SystemExit


title = data.get("title", "AI Future")
scenes = data.get("scenes", [])

if not scenes:
    print("ERROR: No scenes were generated.")
    input("Press Enter to exit...")
    raise SystemExit


print()
print("TITLE:", title)
print("SCENES:", len(scenes))
print()


# ============================================================
# 3. CREATE VIDEO SCENES
# ============================================================

scene_files = []

# IMPORTANT:
# We use a RELATIVE textfile path inside FFmpeg.
# This avoids the Windows D: path / colon problem.

for scene in scenes:

    number = int(scene.get("scene_number", len(scene_files) + 1))
    narration = str(scene.get("narration", ""))
    visual = str(scene.get("visual", ""))
    duration = int(scene.get("duration", 6))

    print(f"Creating Scene {number}...")

    # --------------------------------------------------------
    # Create scene text
    # --------------------------------------------------------

    text_file = TEMP_DIR / f"scene_{number}.txt"

    text_content = (
        f"SCENE {number}\n\n"
        f"{visual}\n\n"
        f"{narration}\n\n"
        f"AI SOCIAL MEDIA VIDEO"
    )

    text_file.write_text(
        text_content,
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Output scene
    # --------------------------------------------------------

    output_file = TEMP_DIR / f"scene_{number}.mp4"

    # Use only the filename for textfile.
    # FFmpeg runs from TEMP_DIR, so no D: path is needed.

    relative_text_file = f"scene_{number}.txt"
    relative_output_file = f"scene_{number}.mp4"

    # Escape the colon in the Windows font path.
    font_path = r"C\:/Windows/Fonts/arial.ttf"

    filter_string = (
        f"drawtext="
        f"fontfile='{font_path}':"
        f"textfile='{relative_text_file}':"
        f"fontcolor=white:"
        f"fontsize=48:"
        f"line_spacing=18:"
        f"x=(w-text_w)/2:"
        f"y=(h-text_h)/2:"
        f"box=1:"
        f"boxcolor=black@0.65:"
        f"boxborderw=40"
    )

    command = [
        "ffmpeg",
        "-y",

        "-f",
        "lavfi",

        "-i",
        "color=c=0x111827:s=1080x1920:r=30",

        "-t",
        str(duration),

        "-vf",
        filter_string,

        "-c:v",
        "libx264",

        "-pix_fmt",
        "yuv420p",

        "-an",

        relative_output_file
    ]

    process = subprocess.run(
        command,
        cwd=str(TEMP_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True
    )

    if process.returncode != 0:

        print()
        print("======================================")
        print("FFMPEG ERROR")
        print("======================================")
        print(process.stderr)
        print()

        input("Press Enter to exit...")
        raise SystemExit

    scene_files.append(output_file)


# ============================================================
# 4. COMBINE ALL SCENES
# ============================================================

print()
print("[3/4] Combining all scenes...")
print()

concat_file = TEMP_DIR / "concat.txt"

with open(
    concat_file,
    "w",
    encoding="utf-8"
) as f:

    for scene_file in scene_files:

        # Use only filenames to avoid Windows drive-letter issues
        f.write(
            f"file '{scene_file.name}'\n"
        )


final_video = VIDEO_DIR / "final_ai_video.mp4"

# FFmpeg concat also runs from TEMP_DIR.
command = [
    "ffmpeg",
    "-y",

    "-f",
    "concat",

    "-safe",
    "0",

    "-i",
    "concat.txt",

    "-c",
    "copy",

    str(final_video)
]

process = subprocess.run(
    command,
    cwd=str(TEMP_DIR),
    stdout=subprocess.DEVNULL,
    stderr=subprocess.PIPE,
    text=True
)

if process.returncode != 0:

    print()
    print("======================================")
    print("FINAL VIDEO ERROR")
    print("======================================")
    print(process.stderr)
    print()

    input("Press Enter to exit...")
    raise SystemExit


# ============================================================
# SUCCESS
# ============================================================

print()
print("[4/4] VIDEO CREATED SUCCESSFULLY!")
print()

print("======================================")
print(" FINAL VIDEO READY")
print("======================================")
print()

print("Title:")
print(title)

print()

print("Video:")
print(final_video)

print()

print("Resolution: 1080 x 1920")
print("Format: MP4")
print("Scenes:", len(scene_files))
print("AI Model: Llama 3.2")
print("AI Engine: Ollama")
print("Video Engine: FFmpeg")

print()
print("======================================")
print()

input("Press Enter to close...")