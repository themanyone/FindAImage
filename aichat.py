#!/usr/bin/python
import io
import base64
import gradio as gr
from PIL import Image
from openai import OpenAI
license = """    AI Chat Interface
    Copyright (C) 2024 Henry F Kroll III, www.thenerdshow.com

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
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA."""

client = OpenAI(base_url="http://localhost:8087/v1", api_key="llama.cpp")

# Get available models initially
models = [model.id for model in client.models.list()]

def predict(prompt, history, model, image=None):
    print(f"Received image: {image}")  # Debugging line
    messages = []
    print(f"Model in use: {model}")
    print()

    # Add previous messages to the conversation history
    for user_message, assistant_message in history:
        messages.append({"role": "user", "content": user_message})
        messages.append({"role": "assistant", "content": assistant_message})

    if image is not None:
        image = image.resize((250, 250))
        # Convert the image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        # Create the data URL
        image_url = f"data:image/png;base64,{image_base64}"

        # Include the image URL and text message separately
        messages.append({"role": "user", "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            },
                        },
                        {"type": "text", "text": prompt},
                    ]})  # Image URL inside
    else:
        messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model, messages=messages, stream=True,
        stop=["<|im_end|>", "###"]
    )

    full_response = ""  # Store the complete response
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            full_response += content

    return full_response  # Return the complete response as a string

JS = """function () {
  gradioURL = window.location.href
  if (!gradioURL.endsWith('?__theme=dark')) {
    window.location.replace(gradioURL + '?__theme=dark');
  }
}"""
CSS = """
footer {
    visibility: hidden;
}
.contain { display: flex; flex-direction: column; }
.gradio-container { height: 100vh !important; }
body { height: 100%; }
#component-1,#component-2 { height: 100% !important; }
#chatbot { flex-grow: 1; overflow: auto;}
"""

with gr.Blocks(theme=gr.themes.Soft(), js=js, css=css, fill_height=True) as demo:
    with gr.Row(equal_height=False):
        with gr.Column(scale=5):
            chat_interface = gr.ChatInterface(
                fn=lambda message, history: predict(message, history, model_dropdown.value, image_input.value),  # Pass the selected model and image
                fill_height=True,
                examples=[
                    "What is the capital of France?",
                    "Who was the first person on the moon?",
                    "Describe this image in 10-50 words.",
                ],
            )

        with gr.Column(scale=1):
            model_dropdown = gr.Dropdown(
                choices=models,
                label="Select Model",
                value=models[0],
                interactive=True
            )
            # Add an image upload component
            image_input = gr.Image(type="pil", label="Upload Image", interactive=True)


    # Connect the model_dropdown to the chat_interface
    def update_chatbot(model, image=None):
        chat_interface.fn = lambda message, history: predict(message, history, model, image)

    model_dropdown.change(
        fn=update_chatbot,
        inputs=[model_dropdown, image_input],
        outputs=None
    )

    image_input.change(
        fn=update_chatbot,
        inputs=[model_dropdown, image_input],
        outputs=None
    )

if __name__ == "__main__":
    demo.launch()
