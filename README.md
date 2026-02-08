**When you can’t call for help, Lifeline calls for you.**'

Lifeline is an AI-powered **voice-based emergency detection system** that listens for signs of distress and automatically alerts a trusted contact. Instead of relying on the user to press a panic button, Lifeline detects emergencies through spoken context and responds autonomously.


## Project Overview

**An audio-based safety monitoring system that detects distress sounds and automatically alerts a contact.**
This project continuously listens for specific voice patterns (e.g., calls for help). When detected, it can trigger actions such as sending an SMS or placing a phone call.

**Note:** The current version detects **voice distress signals only*. It does *not* yet detect physical events such as falls or impacts.

## How It Works

1. The system records short audio clips at regular intervals.

2. Audio is analyzed for distress keywords or patterns.

3. If a trigger condition is met:
  - An SMS alert is sent.
  - A phone call can be initiated.
4. A cooldown period prevents repeated alerts.

## Features

- Continuous voice monitoring
- Automatic SMS alerts
- Optional phone call trigger
- Configurable cooldown period
- Lightweight and runs locally

## Current Limitations

- Detects **voice** only (no fall or motion detection yet)
- Accuracy depends on microphone quality and environmental noise
- Requires proper setup of SMS/call service

## Future Improvements

- Fall detection using motion sensors
- Impact sound recognition
- Machine learning–based voice classification
- Mobile integration
