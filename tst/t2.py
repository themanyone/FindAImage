import base64
import requests
import json

# Path to your audio file
audio_path = "test.wav"  # e.g., "sample.wav"

# Read and encode the audio file to base64
with open(audio_path, "rb") as audio_file:
    audio_data = audio_file.read()
    audio_base64 = base64.b64encode(audio_data).decode("utf-8")

# Define the query payload
payload = {
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Transcribe this audio."
                },
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": audio_base64,
                        "format": "wav"  # Adjust to match your audio file format
                    }
                }
            ]
        }
    ],
    "model": "ultravox-v0_5-llama-3_2-1b",
    "max_tokens": 500,
    "temperature": 0.7,
    "stream": False
}

# Send the request to the server
url = "http://localhost:8087/v1/chat/completions"
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()  # Raise an error for bad status codes
    print("Response:")
    print(json.dumps(response.json(), indent=2))
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
