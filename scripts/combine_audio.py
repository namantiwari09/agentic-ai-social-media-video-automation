import subprocess
from pathlib import Path

BASE = Path(r"D:\agentic-social-media-ai")
AUDIO = BASE / "audio"
VIDEOS = BASE / "videos"
TEMP = BASE / "output" / "audio_temp"

TEMP.mkdir(parents=True, exist_ok=True)

print()
print("======================================")
print(" AUDIO + VIDEO COMBINER")
print("======================================")
print()

# Create FFmpeg concat file
concat_file = TEMP / "audio_concat.txt"

with open(concat_file, "w", encoding="utf-8") as f:
    for i in range(1, 6):
        audio_file = AUDIO / f"scene_{i}.mp3"
        f.write(f"file '{audio_file.as_posix()}'\n")

combined_audio = TEMP / "combined_voice.mp3"

print("[1/2] Combining voiceover scenes...")

command = [
    "ffmpeg",
    "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", str(concat_file),
    "-c", "copy",
    str(combined_audio)
]

result = subprocess.run(
    command,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.PIPE,
    text=True
)

if result.returncode != 0:
    print("ERROR COMBINING AUDIO")
    print(result.stderr)
    input("Press Enter to close...")
    raise SystemExit

print("Voiceover combined successfully.")

# Add audio to video
input_video = VIDEOS / "final_ai_video.mp4"
output_video = VIDEOS / "final_ai_video_with_voice.mp4"

print()
print("[2/2] Adding voiceover to video...")

command = [
    "ffmpeg",
    "-y",
    "-i", str(input_video),
    "-i", str(combined_audio),
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-c:v", "copy",
    "-c:a", "aac",
    "-shortest",
    str(output_video)
]

result = subprocess.run(
    command,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.PIPE,
    text=True
)

if result.returncode != 0:
    print("ERROR ADDING AUDIO")
    print(result.stderr)
    input("Press Enter to close...")
    raise SystemExit

print()
print("======================================")
print(" FINAL VIDEO CREATED SUCCESSFULLY!")
print("======================================")
print()
print("Video:")
print(output_video)
print()
print("Video + AI Voiceover")
print("Resolution: 1080 x 1920")
print("Format: MP4")
print()
print("======================================")
print()

input("Press Enter to close...")