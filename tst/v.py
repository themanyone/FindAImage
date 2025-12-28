import base64
from openai import OpenAI
client = OpenAI(base_url="http://localhost:8087/v1", api_key="llama.cpp")
with open("/home/k/Videos/craps.mp4", "rb") as f:
    video_base64 = base64.b64encode(f.read()).decode("utf-8")
response = client.chat.completions.create(
    model="SkyCaptioner-V1-GGUF:iq2_xs",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this video."},
            {"type": "input_video", "input_video": {"data": video_base64, "format": "mp4"}}
        ]
    }],
    max_tokens=500,
    stream=False
)
print(response.choices[0].message.content)
