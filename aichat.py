#!/usr/bin/python
"""Module: AI Chat Interface
Description: This module defines the interface and server for an artificial 
intelligence-powered chat system. It features image queries and a rating system in 
addition to the usual chat functions."""
import io
import base64
from pprint import pprint
import gradio as gr
from openai import OpenAI

LICENSE = """    AI Chat Interface
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
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
    """

client = OpenAI(base_url="http://localhost:8087/v1", api_key="llama.cpp")

# Get available models initially
models = [model.id for model in client.models.list()]

JS = """function () {
  gradioURL = window.location.href
  if (!gradioURL.endsWith('?__theme=dark')) {
    window.location.replace(gradioURL + '?__theme=dark');
  }
}"""
CSS = """
"""

def predict(prompt, history: list):
    """Module:predict
    
    :param prompt: User message to the chatbot
    :param history: List of messages
    :returns: Chat responses"""
    if demo.image is not None:
        img = demo.image.resize((250, 250))
        # Convert the image to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        # Create the data URL
        image_url = f"data:image/png;base64,{image_base64}"

        # Include the image URL and text message separately
        history.append({"role": "user", "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            },
                        },
                        {"type": "text", "text": prompt},
                    ]})  # Image URL inside
    else:
        history.append({"role": "user", "content": prompt})
    pprint(history)
    response = client.chat.completions.create(
        model=demo.model, messages=history, stream=True,
        stop=["<|im_end|>", "###"]
    )

    history.append({"role": "assistant", "content": ""})
    for tok in response: # pylint: disable=not-an-iterable
        content = tok.choices[0].delta.content
        if content:
            history[-1]['content'] += content.replace('\n', '<br>')
            yield history[-1]

# from https://www.gradio.app/main/docs/gradio/chatinterface
def vote(data: gr.LikeData):
    """Module vote:
    
    :param data: gradio like data"""
    if data.liked:
        print("You upvoted this response: " + data.value[0])
    else:
        print("You downvoted this response: " + data.value[0])

with gr.Blocks(theme=gr.themes.Soft(), js=JS, css=CSS, fill_width=True,
fill_height=True, title="Local AI Chat - FindAImage") as demo:
    demo.model = models[0]
    demo.image = None
    with gr.Row(equal_height=False):
        with gr.Column(scale=8):
            chat_interface = gr.ChatInterface(type="messages",
                fn=predict,
                chatbot=gr.Chatbot(type="messages",
                    height="calc(100vh - 140px)",
                    show_copy_button=True,
                    placeholder="<strong>AI Chatbot</strong><br>Ask Me Anything"),
                fill_height=True,
                examples=[
                    "What is the capital of France?",
                    "Who was the first person on the moon?",
                    "Describe this image in 10-50 words."
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
                # Add an image upload component
                image_input = gr.Image(type="pil", label="Upload Image",
                min_width=320, interactive=True)

                html_output = gr.HTML("""
        <div style='height: 100%; background: #234; padding: 20px; color: white; text-align: center;'>
        <p>
            <a style="color: white" href="https://www.paypal.com/donate/?hosted_button_id=A37BWMFG3XXFG">Support further development</a>
        </p><p>
            <a href="https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html">LICENSE</a>
        </p>
        </div>
        """)

        def update_model(input_model, input_image):
            """
            Module: update_model(model, image)
            
            :model input_model: the model to chat with
            :param input_image: an optional image to analyze
            :returns: None
            """
            demo.model = input_model
            demo.image = input_image

        model_dropdown.change( # pylint: disable=no-member
            fn=update_model,
            inputs=[model_dropdown, image_input],
            outputs=None
        )

        image_input.change( # pylint: disable=no-member
            fn=update_model,
            inputs=[model_dropdown, image_input],
            outputs=None
        )

if __name__ == "__main__":
    demo.launch()
