from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Lifeline AI running"}

# This exposes your audio files publicly
app.mount("/audio", StaticFiles(directory="."), name="audio")