import cv2
import numpy as np
from PIL import Image, ImageEnhance
import os
import time
import pygame
import sys
import csv

os.environ["OPENCV_VIDEOIO_MMAL_ENABLE"] = "1"

pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

SOUNDS_DIR = "sounds"
IN_SOUND = os.path.join(SOUNDS_DIR, "good_serve.mp3")
OUT_SOUND = os.path.join(SOUNDS_DIR, "bad_serve.mp3")
UNKNOWN_SOUND = os.path.join(SOUNDS_DIR, "no_ball.mp3")

PI_RESOLUTION = (1920, 1080)
PI_DISPLAY_ENABLED = True

def edit_image(image_path, dodge_factor=2.5):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Failed to load image: {image_path}")
    img = cv2.resize(img, PI_RESOLUTION)
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    img_pil = ImageEnhance.Brightness(img_pil).enhance(2)
    img_pil = ImageEnhance.Contrast(img_pil).enhance(2.0)
    img_pil = img_pil.convert('L').convert('RGB')
    img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    return cv2.convertScaleAbs(img, alpha=1.5, beta=30)

def play_sound(result):
    try:
        sound_file = IN_SOUND if result == "IN" else OUT_SOUND if result == "OUT" else UNKNOWN_SOUND
        if not os.path.exists(sound_file):
            print(f"Sound file {sound_file} not found.")
            return
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
        pygame.time.wait(800)
    except Exception as e:
        print(f"Error playing sound: {e}")

def overlay_result_text(image, result, timestamp=""):
    overlay = image.copy()
    output = image.copy()
    h, w = image.shape[:2]

    # Draw semi-transparent box
    cv2.rectangle(overlay, (0, 0), (300, 70), (0, 0, 0), -1)
    alpha = 0.6
    cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)

    # Result text
    color = (0, 255, 0) if result == "IN" else (0, 0, 255) if result == "OUT" else (255, 0, 0)
    cv2.putText(output, result, (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)

    # Optional: timestamp
    if timestamp:
        cv2.putText(output, f"Time: {timestamp}s", (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)

    return output

def main():
    print(f"Running on Raspberry Pi with optimised settings: {PI_RESOLUTION}")

    if not os.path.exists(SOUNDS_DIR) or not all(os.path.exists(f) for f in [IN_SOUND, OUT_SOUND, UNKNOWN_SOUND]):
        print("Sound files not found. Run generate_sounds.py to create them.")

    print("\n" + "="*60)
    print(" SQUASH HAWK-EYE BALL DETECTION ".center(60, "="))
    print("="*60)

    output_dir = 'output-screenshots'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_folder = 'impact_screenshots'
    if not os.path.exists(image_folder):
        print(f"Error: Directory '{image_folder}' not found.")
        return

    image_files = sorted([
        f for f in os.listdir(image_folder)
        if f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ])

    if not image_files:
        print(f"No images found in {image_folder} directory!")
        return

    results = []

    for i, image_file in enumerate(image_files):
        print(f"\nProcessing impact {i+1} of {len(image_files)}: {image_file}")

        image_path = os.path.join(image_folder, image_file)
        output_path = f"{output_dir}/output_{i+1}.png"

        try:
            dodge_image = edit_image(image_path, dodge_factor=2.0)
            cv2.imwrite(output_path, dodge_image)

            image = cv2.imread(output_path)
            if image is None:
                print(f"Failed to load '{output_path}'")
                continue

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=20,
                                       param1=30, param2=11, minRadius=5, maxRadius=7)
            edges = cv2.Canny(gray, 30, 130, apertureSize=3)
            lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=30, maxLineGap=5)

            line_y_values = []
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    line_y_values += [y1, y2]
                    cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 1)

            result = "UNKNOWN"
            if line_y_values:
                top_line_y = min(line_y_values)
                cv2.line(image, (0, top_line_y), (image.shape[1], top_line_y), (0, 0, 255), 2)
                if circles is not None:
                    circles = np.uint16(np.around(circles))
                    for (x, y, r) in circles[0, :]:
                        cv2.circle(image, (x, y), r, (0, 255, 0), 1)
                        cv2.circle(image, (x, y), 2, (0, 0, 255), 1)
                        if (y + r) <= (top_line_y + 1):
                            result = "IN"
                        else:
                            result = "OUT"
                        print(f"Ball at (X={x}, Y={y}) is {result}")
                else:
                    print("No ball detected in this image")
                    result = "NO BALL"

            timestamp = image_file.split('_')[-1].replace('sec.jpg', '')
            image = overlay_result_text(image, result, timestamp)

            final_path = f"{output_dir}/result_{i+1}_{result}.png"
            cv2.imwrite(final_path, image)
            play_sound(result)

            if PI_DISPLAY_ENABLED:
                cv2.namedWindow("Analysis", cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty("Analysis", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                cv2.imshow("Analysis", image)
                cv2.waitKey(1200)

            results.append({'image': image_file, 'timestamp': timestamp, 'result': result})

        except Exception as e:
            print(f"Error processing image {image_file}: {e}")

    # Write CSV
    csv_path = os.path.join(output_dir, "results_summary.csv")
    with open(csv_path, "w", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["image", "timestamp", "result"])
        writer.writeheader()
        writer.writerows(results)

    # Summary
    print("\nAnalysis Summary:")
    print("=" * 50)
    for i, r in enumerate(results):
        print(f"Impact {i+1} at {r['timestamp']}s: {r['result']}")
    print("\nCSV saved to:", csv_path)

    if PI_DISPLAY_ENABLED:
        print("\nAnalysis complete! Press any key to exit...")
        cv2.namedWindow("Done", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Done", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        last_image = cv2.imread(final_path) if 'final_path' in locals() else np.zeros((1080, 1920, 3), dtype=np.uint8)
        cv2.imshow("Done", last_image)  
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
