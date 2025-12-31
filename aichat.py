#!/usr/bin/env python
"""Module: AI Chat Interface
Description: This module defines the interface and server for an artificial 
intelligence-powered chat system. It features image and audio queries and a rating 
system in addition to the usual chat functions. This interface is different in that 
the resulting chat text is editable. Just click on it a couple times."""
import io
import base64
import os
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
JS = """function () {
  document.addEventListener('keyup', function(e) {
    if (e.keyCode === 32) {
      document.execCommand('insertHTML', false, ' ');
    }
  });
  window.makeEditable = function(){
    document.querySelectorAll('.chatbot').forEach(function(element) {
      codes = element.querySelectorAll('code');
      codes.forEach(e=>{e.innerText = e.innerText.replaceAll('<br>', '\\n');});
      element.contentEditable = 'true';
      var pe = element.parentElement.parentElement.parentElement;
      var ns = pe.parentElement.nextElementSibling.firstElementChild;
      if (ns.lastElementChild.name != 'ChatThis') {
          var button = document.createElement('button');
          button.textContent = 'Submit';
          button.name = 'ChatThis';
          button.onclick = function() {
            var content = element.innerText;
            // Submit the content using AJAX or a form
            var ic = document.querySelector('.input-container');
            ic.firstElementChild.value += content;
            console.log(content);
          };
          ns.appendChild(button);
       }
    });
  }
}
"""
CSS = """

"""

def get_system_prompt(model_name: str) -> str:
    """Module: get_system_prompt
    :param model_name: Name of the model
    :returns: Appropriate system prompt for the model"""
    # get model capabilities from /props endpoint
    response = requests.get(f'{LLAVA_ENDPOINT[:-2]}props', timeout=5)
    response.raise_for_status()
    response_content = response.json()
    modalities = response_content.get('modalities', {})
    multimodal = False
    if modalities:
        vision = modalities.get('vision', None)
        audio = modalities.get('audio', None)
        print(f"Model capabilities: vision={vision}, audio={audio}")
        if vision or audio:
            multimodal = True
    else:
        # get model args from /models endpoint
        models = client.models.list()
        model_info = next((m for m in models if m.id == model_name), None)
        print(model_info)
        if "status" in model_info and "args" in model_info.status:
            args = model_info.status["args"]
            if "--mmproj" in args:
                multimodal = True
    if multimodal:
        return "You are an AI assistant with multimodal capabilities. You will be provided with images or audio to help answer the user's questions. Provide detailed and accurate responses based on the input data."
    else:
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
            max_tokens=500,
            temperature=0.7,
            stream=True,
            stop=["<|im_end|>", "###"]
        )

        history.append({"role": "assistant", "content": ""})
        for tok in response:  # pylint: disable=not-an-iterable
            content = tok.choices[0].delta.content
            if content:
                history[-1]['content'] += content.replace('\n', '<br>')
                yield history[-1]
    except Exception as e:
        history.append({"role": "assistant", "content": f"Error: {str(e)}".replace('\n', '<br>')})
        yield history[-1]
    # pprint(history)

def vote(data: gr.LikeData):
    """Module vote:
    
    :param data: gradio like data"""
    if data.liked:
        print("You upvoted this response: " + data.value[0])
    else:
        print("You downvoted this response: " + data.value[0])

with gr.Blocks() as demo:
    if len(models) == 0:
        exit(1)
    demo.model = models[0]
    demo.image = None
    demo.audio = None
    with gr.Row(equal_height=False):
        with gr.Column(scale=8):
            chat_interface = gr.ChatInterface(
#                type="messages",
                fn=predict,
                chatbot=gr.Chatbot(
#                    type="messages",
                    height="calc(100vh - 140px)",
#                    show_copy_button=True,
                    placeholder="<strong>AI Chatbot</strong><br>Ask Me Anything"
                ),
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
                html_output = gr.HTML("""
        <div style='height: 100%; background: #234; padding: 20px; color: white; text-align: center;'>
        <p>
            <a style="color: white" href="https://www.paypal.com/donate/?hosted_button_id=A37BWMFG3XXFG">Support further development</a>
        </p><p>
            <a href="https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html">LICENSE</a>
        </p>
        </div>
        """)

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

    gr.on(
        triggers=[chat_interface.chatbot.select],
        fn=lambda: None,
        inputs=None,
        outputs=None,
        js="""function(){
          makeEditable();
        }"""
    )

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft(), js=JS, css=CSS)
