import os
import time
import traceback
import sounddevice as sd
from scipy.io.wavfile import write
import whisper
from google import genai
from elevenlabs.client import ElevenLabs
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TWILIO_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
EMERGENCY_CONTACT = os.getenv("EMERGENCY_CONTACT")
NGROK_URL = os.getenv("NGROK_URL")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Setup APIs
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
eleven_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

# Whisper setup
os.environ["PATH"] += os.pathsep + r"C:\Users\maxya\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"

fs = 16000
seconds = 5
model = whisper.load_model("tiny")

STATE_MONITORING = "monitoring"
STATE_COOLDOWN = "cooldown"

state = STATE_MONITORING
last_alert_time = 0

COOLDOWN_SECONDS = 30  # change to 30 for testing, 120 for production

# Audio capture
def record_chunk(filename="input.wav", device=None):
    try:
        print("Recording audio chunk...", flush=True)
        audio = sd.rec(int(seconds * fs), samplerate=fs, channels=1, device=device)
        sd.wait()
        filepath = os.path.join(os.getcwd(), filename)
        write(filepath, fs, audio)
        print(f"Saved audio to {filepath}", flush=True)
        return filepath
    except Exception as e:
        print("Error during recording:", flush=True)
        traceback.print_exc()
        return None

# Transcription
def transcribe_audio(filename):
    try:
        result = model.transcribe(filename)
        print("Transcript:", result["text"], flush=True)
        return result["text"]
    except Exception as e:
        print("Error during transcription:", flush=True)
        traceback.print_exc()
        return ""

# Gemini emergency detection
def generate_emergency_message(transcript, name="Max", location="STC at the University of Waterloo"):
    try:
        prompt = f"""
You are a life-saving AI assistant.
Given the transcript of spoken audio:

\"\"\"{transcript}\"\"\"

If this is an emergency, generate a concise descriptive emergency alert
for audio playback, including the person's name ({name}) and location ({location}).
If not, respond with "NO EMERGENCY".
"""
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        print("Gemini message:", response.text.strip(), flush=True)
        return response.text.strip()
    except Exception as e:
        print("Error during Gemini processing:", flush=True)
        traceback.print_exc()
        return "NO EMERGENCY"

# ElevenLabs TTS
def create_emergency_audio(message, filename="emergency.mp3"):
    try:
        print("Generating audio with ElevenLabs...", flush=True)
        audio_stream = eleven_client.text_to_speech.convert(
            voice_id="21m00Tcm4TlvDq8ikWAM",
            model_id="eleven_multilingual_v2",
            text=message
        )
        with open(filename, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)
        print(f"Saved emergency audio to {filename}", flush=True)
        return filename
    except Exception as e:
        print("Error during audio generation:", flush=True)
        traceback.print_exc()
        return None

# Twilio SMS + call
def send_twilio_alert(message):
    try:
        print("Sending SMS and call via Twilio...", flush=True)
        sms = twilio_client.messages.create(
            body=message,
            from_=TWILIO_NUMBER,
            to=EMERGENCY_CONTACT
        )
        print("SMS sent:", sms.sid, flush=True)

        call = twilio_client.calls.create(
            to=EMERGENCY_CONTACT,
            from_=TWILIO_NUMBER,
            twiml=f"<Response><Play>{NGROK_URL}</Play></Response>"
        )
        print("Call initiated:", call.sid, flush=True)
    except Exception as e:
        print("Error during Twilio alert:", flush=True)
        traceback.print_exc()

# Main loop
cooldown = 60
last_alert_time = 0

print("Lifeline AI monitoring started...", flush=True)

while True:
    try:
        if state == STATE_MONITORING:

            audio_file_path = record_chunk()
            if not audio_file_path:
                time.sleep(1)
                continue

            transcript = transcribe_audio(audio_file_path)
            if not transcript.strip():
                time.sleep(1)
                continue

            message = generate_emergency_message(transcript)

            if message != "NO EMERGENCY":
                current_time = time.time()
                if current_time - last_alert_time > cooldown:
                    emergency_mp3 = create_emergency_audio(message)
                    if emergency_mp3:
                        send_twilio_alert(message)
                        last_alert_time = current_time
                    state = STATE_COOLDOWN
                else:
                    print("Emergency detected but still in cooldown.", flush=True)
            else:
                print("No emergency detected.", flush=True)

            time.sleep(1)
        elif state == STATE_COOLDOWN:

            remaining = int(COOLDOWN_SECONDS - (time.time() - last_alert_time))

            if remaining > 0:
                print(f"Cooldown active... {remaining}s remaining", flush=True)
                time.sleep(5)
            else:
                print("Cooldown finished. Returning to monitoring.", flush=True)
                state = STATE_MONITORING
    except Exception as e:
        print("Error in main loop:", flush=True)
        traceback.print_exc()
        time.sleep(5)
