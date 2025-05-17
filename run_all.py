import subprocess
import os
import sys
import time


def clean_video(input_path, output_path):
    print(f"[INFO] Cleaning video for FFmpeg compatibility...")
    cmd = [
        "ffmpeg",
        "-y",  # overwrite output if exists
        "-i", input_path,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "18",
        output_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print("[ERROR] FFmpeg failed to clean the video:")
        print(result.stderr)
        raise RuntimeError("Video conversion failed")
    else:
        print("[INFO] Video cleaned successfully.")


def check_dependencies():
    missing_deps = []

    try:
        import pygame
    except ImportError:
        missing_deps.append("pygame")

    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")

    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")

    try:
        from PIL import Image
    except ImportError:
        missing_deps.append("pillow")

    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        missing_deps.append("ffmpeg")

    try:
        subprocess.run(["java", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        missing_deps.append("java")

    return missing_deps


def generate_sounds():
    sounds_dir = "sounds"
    os.makedirs(sounds_dir, exist_ok=True)

    sound_files = [
        os.path.join(sounds_dir, "in.mp3"),
        os.path.join(sounds_dir, "out.mp3"),
        os.path.join(sounds_dir, "unknown.mp3")
    ]

    if not all(os.path.exists(f) for f in sound_files):
        print("\nGenerating sound files...")
        if os.path.exists("generate_sounds.py"):
            subprocess.run([sys.executable, "generate_sounds.py"])
        else:
            print("Warning: generate_sounds.py not found. Sound files will be missing.")


def setup_directories():
    dirs = ["impact_screenshots", "output-screenshots"]
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    print("Directories prepared.")


def main():
    print("\n" + "="*70)
    print(" SQUASH HAWK-EYE SYSTEM ".center(70, "="))
    print("="*70)

    # Check dependencies
    print("\nChecking system dependencies...")
    missing = check_dependencies()
    if missing:
        print(f"Warning: The following dependencies are missing: {', '.join(missing)}")
        proceed = input("Do you want to continue anyway? (y/n): ")
        if proceed.lower() != 'y':
            print("Exiting.")
            return
    else:
        print("All dependencies found.")

    # Generate sound files if needed
    generate_sounds()

    # Set up directories
    setup_directories()

    # ✅ Fix path string
    default_video = r"C:\Users\Somaan\Downloads\audio-video-project\audio-video-project\com\p014\test_8.mp4"
    cleaned_video = os.path.splitext(default_video)[0] + "_cleaned.mp4"

    clean_video(default_video, cleaned_video)

    if not os.path.exists(default_video):
        print(f"\nDefault video '{default_video}' not found.")
        print("You'll be prompted to select a video when the application starts.")
    else:
        print(f"\nUsing default video: {default_video}")

    # ✅ Compile Java class
    print("\nCompiling Java class...")
    java_dir = r"C:\Users\Somaan\Downloads\audio-video-project\audio-video-project"
    os.chdir(java_dir)  # Ensure we're in the correct folder
    compile_proc = subprocess.run(["javac", "SquashHawkeye.java"])
    if compile_proc.returncode != 0:
        print("Compilation failed. Ensure you're in the right directory with SquashHawkeye.java.")
        return
    
    # ✅ Run Java class once (after compiling)
    print("\nStarting impact detection...")
    try:
        print(f"[DEBUG] java SquashHawkeye {default_video}")
        java_process = subprocess.Popen(["java", "SquashHawkeye", default_video])
        java_process.wait()
        print("Impact detection complete.")
    except Exception as e:
        print(f"Error running Java application: {e}")
        return

    screenshot_count = 0
    if os.path.exists("impact_screenshots"):
        screenshot_count = len([f for f in os.listdir("impact_screenshots")
                                if f.lower().endswith(('.png', '.jpg', '.jpeg'))])

    if screenshot_count == 0:
        print("No impact screenshots were captured. Exiting.")
        return

    print(f"\nFound {screenshot_count} impact screenshots.")
    time.sleep(1)

    print("\nRunning ball detection analysis...")
    try:
        subprocess.run([sys.executable, "cv_ball_detection.py"])
    except Exception as e:
        print(f"Error running ball detection: {e}")

    print("\nSquash Hawk-Eye analysis complete!")


if __name__ == "__main__":
    main()
