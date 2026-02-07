from elevenlabs.client import ElevenLabs
import os
from dotenv import load_dotenv

load_dotenv()

client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY")
)

def generate_emergency_audio(text, filename="emergency.mp3"):
    audio = client.text_to_speech.convert(
        voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel voice
        model_id="eleven_multilingual_v2",
        text=text
    )

    with open(filename, "wb") as f:
        for chunk in audio:
            f.write(chunk)

    return filename