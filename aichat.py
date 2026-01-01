#!/usr/bin/env python
"""Module: AI Chat Interface
Description: This module defines the interface and server for an artificial 
intelligence-powered chat system. It features image and audio queries and a rating 
system in addition to the usual chat functions. This interface is different in that 
the resulting chat text is editable. Just click on it a couple times."""
import html
import io
import base64
import json
import os
import time
import requests
from pprint import pprint
import gradio as gr
from openai import OpenAI
import librosa
import soundfile as sf
LLAVA_ENDPOINT = "http://localhost:8087/v1"
model_changed = False

LICENSE = """    AI Chat Interface
    Copyright (C) 2025 Henry F Kroll III, www.thenerdshow.com

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
    """

client = OpenAI(base_url=LLAVA_ENDPOINT, api_key="llama.cpp")

# Get available models initially
try:
    models = [model.id for model in client.models.list()]
    if len(models) == 0:
        print(f"\nNo models found at {LLAVA_ENDPOINT}\n")
except Exception as e:
    print(f"\nERROR retrieving models from {LLAVA_ENDPOINT}: {e}\n")
    models = []
JS = """
"""
CSS = """

"""

def get_system_prompt(model_name: str) -> str:
    """Module: get_system_prompt
    :param model_name: Name of the model
    :returns: Appropriate system prompt for the model"""
    # wait for capabilities from /props endpoint
    for _ in range(10):
        try:
            response = requests.get(f'{LLAVA_ENDPOINT[:-2]}props?model={model_name}', timeout=5)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException:
            time.sleep(1)
    response.raise_for_status()
    response_content = response.json()
    modalities = response_content.get('modalities', {})
    multimodal = False
    if modalities:
        vision = modalities.get('vision', None)
        audio = modalities.get('audio', None)
        print(f"Model capabilities: vision={vision}, audio={audio}")
        if vision and audio:
            return "You are an AI assistant with multimodal capabilities. You will be provided with images or audio to help answer the user's questions. Provide detailed and accurate responses based on the input data."
        if vision:
            return "You are an AI assistant with image understanding capabilities. You will be provided with images to help answer the user's questions. Provide detailed and accurate responses based on the input data."
        if audio:
            return "You are an AI assistant with audio understanding capabilities. You will be provided with audio to help answer the user's questions. Provide detailed and accurate responses based on the input data."
    else:
        # get model args from /models endpoint
        models = client.models.list()
        model_info = next((m for m in models if m.id == model_name), None)
        if "args" in model_info.status:
            args = model_info.status["args"]
            if "--mmproj" in args:
                multimodal = True
                # print(f"Model supports multimodal input.")
    if multimodal:
        return "You are an AI assistant with multimodal capabilities. You will be provided with images or audio to help answer the user's questions. Provide detailed and accurate responses based on the input data."
    else:
        # print("Model is text-only.")
        return "You are a helpful AI assistant."

def predict(prompt, history: list):
    """Module: predict
    :param prompt: User message to the chatbot
    :param history: List of messages
    :returns: Chat responses"""
    message_content = []
    global model_changed
    if history ==[] or model_changed:
        system_prompt = get_system_prompt(demo.model)
        # Add system prompt to start new conversation
        history.append({"role": "system", "content": system_prompt})
        model_changed = False

    # Handle text input
    message_content.append({"type": "text", "text": prompt})

    # Handle image input
    if demo.image is not None:
        img = demo.image.resize((250, 250))
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        image_url = f"data:image/png;base64,{image_base64}"
        message_content.append({
            "type": "image_url",
            "image_url": {"url": image_url}
        })

    # Handle audio input
    if demo.audio is not None:
        try:
            # Resample audio to 16000 Hz for Ultravox compatibility
            audio, sr = librosa.load(demo.audio, sr=16000)
            # Save resampled audio to a temporary file
            temp_audio_path = "temp_audio.wav"
            sf.write(temp_audio_path, audio, sr)
            # Read and encode the resampled audio
            with open(temp_audio_path, 'rb') as audio_file:
                audio_bytes = audio_file.read()
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            # Determine audio format (use "wav" for resampled audio)
            audio_format = "wav"
            message_content.append({
                "type": "input_audio",
                "input_audio": {
                    "data": audio_base64,
                    "format": audio_format
                }
            })
            # Clean up temporary file
            os.remove(temp_audio_path)
        except Exception as e:
            message_content.append({
                "type": "text",
                "text": f"[Audio Error]: Failed to process audio: {str(e)}"
            })
            print(e)

    # Append to history
    history.append({"role": "user", "content": message_content})

    # Send request to the server
    try:
        response = client.chat.completions.create(
            model=demo.model,
            messages=history,
            temperature=0.2,
            stream=True,
        )

        history.append({"role": "assistant", "content": ""})
        start_time = time.time()
        token_count = 0

        for tok in response:                     # streamed tokens
            content = tok.choices[0].delta.content
            if content:
                history[-1]["content"] += html.unescape(content)
                token_count += 1
                # Yield only the assistant message (first output)
                yield history[-1]

        token_count *= 2.75  # approximate
        elapsed = time.time() - start_time
        tps = token_count / elapsed if elapsed > 0 else 0
        tps_str = f"{tps:.1f} tokens/sec."

        # Yield the final assistant message **and** the TPS string
        yield history[-1], tps_str
    except Exception as e:
        history.append({"role": "assistant", "content": f"Error: {str(e)}".replace('\n', '<br>')})
        yield history[-1], "0 tokens/sec."
    # pprint(history)

# Create global storage for model votes
votes = {}

# Add file path for vote storage
# filepath: /home/k/.local/src/python/FindAImage/votes.json
def load_votes():
    global votes
    if os.path.exists("votes.json"):
        with open("votes.json", "r") as f:
            votes = json.load(f)

def save_votes():
    global votes
    with open("votes.json", "w") as f:
        json.dump(votes, f, indent=2)
    
def vote(data: gr.LikeData):
    """Module vote:
    
    :param data: gradio like data"""
    load_votes()  # Load existing votes
    model_name = demo.model  # Get current model from demo state
    
    # Initialize model entry if needed
    if model_name not in votes:
        votes[model_name] = {"up": 0, "down": 0}
    
    # Update counts
    if data.liked:
        votes[model_name]["up"] += 1
    else:
        votes[model_name]["down"] += 1
    
    save_votes()  # Persist changes

with gr.Blocks() as demo:
    if len(models) == 0:
        exit(1)
    demo.model = models[0]
    demo.image = None
    demo.audio = None
    tps_box = gr.HTML(html_template = """
        <div style='height: 100%; background: #234; padding: 20px; color: white; text-align: center;'>
        <p>${value}</p>
        <p>  
            <a style="color: white" href="https://www.paypal.com/donate/?hosted_button_id=A37BWMFG3XXFG">Support further development</a>
        </p><p>
            <a href="https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html">LICENSE</a>
        </p>
        </div>
        """,
        value="0 tokens/sec.",
        render=False
    )
    with gr.Row(equal_height=False):

        # ---- left‑hand column components ----
        with gr.Column(scale=8):
            
            chat_interface = gr.ChatInterface(
                editable=True,
                fn=predict,
                chatbot=gr.Chatbot(
                    height="calc(100vh - 140px)",
                    placeholder="<strong>AI Chatbot</strong><br>Ask Me Anything"
                ),
                additional_outputs=[tps_box],     
                fill_height=True,
                examples=[
                    "What is the capital of France?",
                    "Who was the first person on the moon?",
                    "Describe this image in 10-50 words.",
                    "Describe this audio in 10-50 words.",
                    "Reply with transcribed audio."
                ]
            ).queue()
            chat_interface.chatbot.like(vote, None, None)

        # ---- right‑hand column components (created first) ----
        with gr.Column(scale=1):
            with gr.Row(equal_height=False):
                # Select model
                model_dropdown = gr.Dropdown(
                    choices=models, label="Select Model", value=models[0],
                    min_width=320, interactive=True
                )
                # Add image upload component
                image_input = gr.Image(
                    type="pil", label="Upload Image",
                    min_width=320, interactive=True
                )
                # Add audio upload component
                audio_input = gr.Audio(
                    type="filepath", label="Upload or Record Audio",
                    min_width=320, interactive=True
                )
                tps_box.render()

        def update_model(input_model, input_image, input_audio):
            """
            Module: update_model(model, image, audio)

            :param input_model: the model to chat with
            :param input_image: an optional image to analyze
            :param input_audio: an optional audio file to analyze
            :returns: None
            """
            if demo.model != input_model:
                # Model has changed, reset image and audio
                global model_changed
                model_changed = True
            demo.model = input_model
            demo.image = input_image
            demo.audio = input_audio
            return None

        model_dropdown.change(
            fn=update_model,
            inputs=[model_dropdown, image_input, audio_input],
            outputs=None
        )
        image_input.change(
            fn=update_model,
            inputs=[model_dropdown, image_input, audio_input],
            outputs=None
        )
        audio_input.change(
            fn=update_model,
            inputs=[model_dropdown, image_input, audio_input],
            outputs=None
        )

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft(), js=JS, css=CSS, )

