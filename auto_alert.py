import os
import time
import sounddevice as sd
from scipy.io.wavfile import write
import whisper
from google.genai import TextGenerationClient
from elevenlabs import set_api_key, generate, save
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# Setup APIs
# -----------------------------
# Gemini
gemini_client = TextGenerationClient()

# ElevenLabs
set_api_key(os.getenv("ELEVENLABS_API_KEY"))

# Twilio
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)
TWILIO_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
EMERGENCY_CONTACT = os.getenv("EMERGENCY_CONTACT")
NGROK_URL = os.getenv("NGROK_URL")  # public FastAPI endpoint serving mp3s

# -----------------------------
# Audio capture & transcription
# -----------------------------
fs = 16000      # sample rate
seconds = 5     # chunk duration
model = whisper.load_model("tiny")  # lightweight, fast

def record_chunk(filename="input.wav"):
    print("Recording audio chunk...")
    audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()
    write(filename, fs, audio)
    return filename

def transcribe_audio(filename):
    result = model.transcribe(filename)
    return result["text"]

# -----------------------------
# Gemini emergency message
# -----------------------------
def generate_emergency_message(transcript, name="Max", location="123 Maple St"):
    prompt = f"""
You are a life-saving AI assistant. 
Given the transcript of spoken audio:

\"\"\"{transcript}\"\"\"

Determine if this is an emergency. If yes, generate a concise but descriptive
emergency alert suitable for audio playback, mentioning the person's name and location.
If it is not an emergency, respond with "NO EMERGENCY".
"""
    response = gemini_client.generate_text(
        model="gemini-1.5-t",
        prompt=prompt,
        max_output_tokens=150
    )
    return response.text.strip()

# -----------------------------
# ElevenLabs audio generation
# -----------------------------
def create_emergency_audio(message, filename="emergency.mp3"):
    audio = generate(
        text=message,
        voice="alloy",
        model="eleven_multilingual_v1"
    )
    save(audio, filename)
    return filename

# -----------------------------
# Twilio call + SMS
# -----------------------------
def send_twilio_alert(message, audio_file):
    # SMS
    sms = twilio_client.messages.create(
        body=message,
        from_=TWILIO_NUMBER,
        to=EMERGENCY_CONTACT
    )
    print("SMS sent:", sms.sid)

    # Call with audio
    call = twilio_client.calls.create(
        to=EMERGENCY_CONTACT,
        from_=TWILIO_NUMBER,
        twiml=f"<Response><Play>{NGROK_URL}/{audio_file}</Play></Response>"
    )
    print("Call initiated:", call.sid)

# -----------------------------
# Main loop
# -----------------------------
cooldown = 60  # seconds between alerts to avoid spamming
last_alert_time = 0

print("Lifeline AI monitoring started...")
while True:
    filename = record_chunk()
    transcript = transcribe_audio(filename)
    print("Transcript:", transcript)

    message = generate_emergency_message(transcript)
    print("Gemini response:", message)

    if message != "NO EMERGENCY":
        current_time = time.time()
        if current_time - last_alert_time > cooldown:
            audio_file = create_emergency_audio(message)
            send_twilio_alert(message, audio_file)
            last_alert_time = current_time
        else:
            print("Emergency detected, but still in cooldown.")
    else:
        print("No emergency detected.")

    # small delay before next chunk
    time.sleep(1)
