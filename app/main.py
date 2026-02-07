from fastapi import FastAPI, UploadFile, File
from app.emergency_logic import analyze_transcript
from app.tts import speak_alert

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Lifeline AI running"}

@app.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    transcript = "I fell and I can't get up"  # placeholder for demo
    
    result = analyze_transcript(transcript)

    if result["is_emergency"]:
        speak_alert("Emergency detected. Contacting help.")

    return result