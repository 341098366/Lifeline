from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

def call_and_play(audio_url, to_number):
    call = client.calls.create(
        to=to_number,
        from_=os.getenv("TWILIO_PHONE_NUMBER"),
        twiml=f"""
        <Response>
            <Play>{audio_url}</Play>
        </Response>
        """
    )

    return call.sid