"""
Generate a narrated demo video showing the REAL application running.

Uses app_demo_sandbox.py to execute IntegrityCheck in an isolated sandbox.
No presentation slides — only live terminal output from the app.

Output: demo_video.mp4
Run: python create_demo_video.py
"""

from pathlib import Path

import numpy as np
import pyttsx3
from moviepy import AudioFileClip, VideoClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

from app_demo_sandbox import build_all_terminal_sessions

PROJECT_DIR = Path(__file__).parent
VIDEO_DIR = PROJECT_DIR / "demo_video_build"
OUTPUT_VIDEO = PROJECT_DIR / "demo_video.mp4"

AUTHORS = "Hassen Moussi & Ahmed Arfaoui"
VIDEO_SIZE = (1280, 720)
FPS = 24

THEME = {
    "navy": (30, 58, 95),
    "teal": (13, 148, 136),
    "sky": (56, 189, 248),
    "green": (5, 150, 105),
    "bg": (248, 250, 252),
    "text": (30, 41, 59),
    "terminal_bg": (15, 23, 42),
    "terminal_text": (226, 232, 240),
    "terminal_user": (250, 204, 21),
    "terminal_cmd": (45, 212, 191),
    "terminal_result": (74, 222, 128),
}


def get_font(size: int, bold: bool = False):
    for path in (
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def get_mono_font(size: int):
    for path in ("C:/Windows/Fonts/consola.ttf", "C:/Windows/Fonts/cour.ttf"):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def line_color(line: str):
    if line.startswith("> "):
        return THEME["terminal_user"]
    if line.startswith("$ "):
        return THEME["terminal_cmd"]
    if any(k in line for k in ("SHA-256", "checksums match", "Result", "Throughput")):
        return THEME["terminal_result"]
    if any(k in line.lower() for k in ("barber", "chunk", "shop full", "processing")):
        return THEME["sky"]
    return THEME["terminal_text"]


def render_app_frame(title: str, subtitle: str, visible_lines: list[str], cursor: bool = False) -> Image.Image:
    img = Image.new("RGB", VIDEO_SIZE, THEME["bg"])
    draw = ImageDraw.Draw(img)

    draw.rectangle((0, 0, VIDEO_SIZE[0], 88), fill=THEME["navy"])
    draw.rectangle((0, 88, VIDEO_SIZE[0], 96), fill=THEME["teal"])
    draw.text((36, 18), "IntegrityCheck", font=get_font(26, bold=True), fill=(255, 255, 255))
    draw.text((36, 50), title, font=get_font(16), fill=THEME["sky"])
    if subtitle:
        draw.text((340, 50), subtitle, font=get_font(14), fill=(200, 220, 240))

    # App window chrome
    win = (36, 110, VIDEO_SIZE[0] - 36, VIDEO_SIZE[1] - 50)
    draw.rounded_rectangle(win, radius=10, fill=THEME["terminal_bg"], outline=THEME["teal"], width=2)
    draw.text((52, 122), "● ● ●  python client.py  —  live application", font=get_mono_font(13), fill=THEME["teal"])

    font = get_mono_font(14)
    line_height = 19
    max_lines = 26
    start_idx = max(0, len(visible_lines) - max_lines)
    display = visible_lines[start_idx:]

    y = 152
    for line in display:
        text = line if len(line) <= 118 else line[:115] + "..."
        draw.text((52, y), text, font=font, fill=line_color(line))
        y += line_height

    if cursor and visible_lines:
        last = visible_lines[-1]
        cx = 52 + int(draw.textlength(last[:118], font=font))
        cy = 152 + (len(display) - 1) * line_height
        draw.rectangle((cx + 4, cy, cx + 12, cy + 15), fill=THEME["terminal_user"])

    draw.rectangle((0, VIDEO_SIZE[1] - 40, VIDEO_SIZE[0], VIDEO_SIZE[1]), fill=THEME["navy"])
    draw.text(
        (36, VIDEO_SIZE[1] - 28),
        f"Live app demo  |  {AUTHORS}  |  sandbox: demo_sample.bin",
        font=get_font(12),
        fill=THEME["sky"],
    )
    return img


def speak(text: str, wav_path: Path) -> None:
    engine = pyttsx3.init()
    engine.setProperty("rate", 168)
    for voice in engine.getProperty("voices"):
        if "zira" in voice.name.lower() or "english" in voice.name.lower():
            engine.setProperty("voice", voice.id)
            break
    engine.save_to_file(text, str(wav_path))
    engine.runAndWait()


def terminal_clip(title: str, subtitle: str, lines: list[str], audio_path: Path) -> VideoClip:
    audio = AudioFileClip(str(audio_path))
    duration = max(audio.duration + 0.5, 5.0)
    total = max(len(lines), 1)

    def make_frame(t):
        progress = min(1.0, t / (duration * 0.92))
        count = max(1, int(progress * total))
        frame = render_app_frame(title, subtitle, lines[:count], cursor=(t < duration - 0.3))
        return np.array(frame)

    return VideoClip(make_frame, duration=duration).with_fps(FPS).with_audio(audio)


SEGMENTS = [
    {
        "id": "01_intro",
        "title": "Client Application",
        "subtitle": "python client.py",
        "session": "intro",
        "narration": (
            f"Welcome to IntegrityCheck, built by {AUTHORS}. "
            "This is our real client application for parallel file integrity verification. "
            "The user opens client dot py and selects how to process a large file."
        ),
    },
    {
        "id": "02_barber",
        "title": "Option 1 — Sleeping Barber",
        "subtitle": "Real chunk processing with bounded queue",
        "session": "sleeping_barber",
        "narration": (
            "The user chooses option one, Sleeping Barber mode. "
            "We set two barber threads and four waiting chairs. "
            "Watch the real application: chunks enter the shop, barbers wake up, "
            "and each chunk is hashed with SHA-256."
        ),
    },
    {
        "id": "03_threads",
        "title": "Option 3 — Multithreading",
        "subtitle": "Configurable worker threads",
        "session": "multithreading",
        "narration": (
            "Next, option three runs multithreading on the same file. "
            "The number of threads is configurable. "
            "The application returns the same file checksum, confirming integrity."
        ),
    },
    {
        "id": "04_benchmark",
        "title": "Option 4 — Benchmark All Modes",
        "subtitle": "Sequential, multiprocessing, multithreading, Sleeping Barber",
        "session": "benchmark",
        "narration": (
            "Option four benchmarks every processing mode on the same file. "
            "The app compares execution time and verifies all checksums match. "
            "A JSON report is saved to processing report dot json."
        ),
    },
    {
        "id": "05_cli",
        "title": "Command Line Interface",
        "subtitle": "parallel_processing.py",
        "session": "cli",
        "narration": (
            "The application can also run from the command line. "
            "Here we launch parallel processing dot py with Sleeping Barber mode. "
            "This is the same engine, usable by scripts and automation."
        ),
    },
    {
        "id": "06_close",
        "title": "Summary",
        "subtitle": "IntegrityCheck demo complete",
        "session": "benchmark",
        "narration": (
            f"Thank you for watching. IntegrityCheck by {AUTHORS} "
            "demonstrates real file processing with multiprocessing, multithreading, "
            "Sleeping Barber synchronization, and SHA-256 integrity verification."
        ),
    },
]


def build_video() -> Path:
    VIDEO_DIR.mkdir(exist_ok=True)

    print("Running application sandbox (real code, isolated demo file)...")
    sessions = build_all_terminal_sessions()

    clips = []
    for index, segment in enumerate(SEGMENTS, start=1):
        seg_id = segment["id"]
        print(f"Segment {index}/{len(SEGMENTS)}: {seg_id}")

        wav_path = VIDEO_DIR / f"{seg_id}.wav"
        speak(segment["narration"], wav_path)

        lines = sessions[segment["session"]]
        if seg_id == "06_close":
            lines = lines[-12:] + ["", "--- Demo complete ---", "File verified. Report saved."]

        clip = terminal_clip(segment["title"], segment["subtitle"], lines, wav_path)
        clips.append(clip)

    print("Rendering demo_video.mp4 ...")
    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(str(OUTPUT_VIDEO), fps=FPS, codec="libx264", audio_codec="aac", logger=None)
    return OUTPUT_VIDEO


def main() -> None:
    output = build_video()
    print(f"\nApplication demo video ready: {output}")
    print("Content: live client.py + CLI runs in sandbox (no presentation slides)")


if __name__ == "__main__":
    main()
