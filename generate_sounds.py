import os
from gtts import gTTS

def generate_sounds():
    """Generate speech files for Good Serve and Bad Serve calls"""
    # Create sounds directory if it doesn't exist
    os.makedirs("sounds", exist_ok=True)
    
    # Generate "Good Serve" sound (IN)
    print("Generating 'Good Serve' sound file...")
    good_serve_tts = gTTS("Good serve", lang='en')
    good_serve_tts.save("sounds/good_serve.mp3")
    
    # Generate "Bad Serve" sound (OUT)
    print("Generating 'Bad Serve' sound file...")
    bad_serve_tts = gTTS("Bad serve", lang='en')
    bad_serve_tts.save("sounds/bad_serve.mp3")
    
    # Generate "No Ball" sound (UNKNOWN)
    print("Generating 'No Ball' sound file...")
    no_ball_tts = gTTS("No ball detected", lang='en')
    no_ball_tts.save("sounds/no_ball.mp3")
    
    print("Sound files generated successfully!")
    
if __name__ == "__main__":
    generate_sounds()
