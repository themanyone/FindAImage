#!/usr/bin/python
from flask import Flask, send_from_directory, render_template_string, jsonify
import io
import os, sys
import base64
#import webbrowser
from PIL import Image
from openai import OpenAI
client = OpenAI()
import google.generativeai as genai
app = Flask(__name__)
from figs import parse_html

ai_model = 'lorem' # default to lorem ipsum
# Local llava-llama.cpp endpoint
LLAVA_ENDPOINT = "http://localhost:8087/v1"
lclient = OpenAI(base_url=LLAVA_ENDPOINT, api_key="sk-xxx")
# "chat_format": "llava-1-5"
models = [model.id for model in lclient.models.list() if "llava" in model.id or "vision" in model.id]
# Google Gemini API endpoint
GEMINI_API_ENDPOINT = "https://api.gemini.google/v1/text"
# Your Gemini API key (export GENAI_TOKEN)
GEMINI_API_KEY = os.environ.get("GENAI_TOKEN")
genai.configure(api_key=GEMINI_API_KEY)
# Configure OpenAI
gpt_key = os.getenv("OPENAI_API_KEY")
OpenAI.api_key = gpt_key
# Existing captions will go here
figures_collection = {}

@app.route('/')
def gallery():
    global figures_collection
    # Get captions (figures_collection) from index.html, if it exists
    file_path = os.path.join(IMAGE_FOLDER, 'index.html')
    if os.path.isfile(file_path):
        figures_collection = parse_html(file_path)
    image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.endswith(('.png', '.jpg', '.jpeg'))]
    return render_template_string('''<head>
        <meta charset="UTF-8"><!--//
    AI Image Gallery.
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
        //-->
        <title>Image Gallery</title>
        <style>
        html {
            height: 100%;
            width: 100%;
        }
        #root {
            height: 100%;
            width: 100%;
            overflow: auto;
        }
        a {
            color: #eee;
            text-decoration: none;
        }
        a:hover {
            color: #ccc;
        }
        body {
            display: flex;
            flex-wrap: wrap;
            justify-content: flex-start;
            margin: 0;
            padding: 0;
            background-color: #333; /* Charcoal gray */
            color: white;
            font-family: arial,verdana,helvetica,sans-serif;
        }
        p {
            font-size:12pt;
        }
        figure {
            width:320px;
            display:inline;
            white-space: nowrap;
        }
        figure:hover{
            white-space: normal;
        }
        figcaption {
            position: relative;
            width: inherit;
            overflow: hidden;
            text-overflow: ellipsis;
            background: #181818;
        }
        header {
            width: 100%;
            background-color: #101010;
        }
        header div * {
            position: relative;
            -webkit-border-radius: 5px;
        }
        header div {
            margin: 0 auto;
            width: 350px;
        }
        .button {
        	background:linear-gradient(to bottom, #e6e6e6 5%, #757575 100%);
        	background-color:#e6e6e6;
        	border-radius:5px;
        	display:inline-block;
        	cursor:pointer;
        	color:#505739;
        	font-family:Arial;
        	font-size:14px;
        	font-weight:bold;
        	padding:5px;
        	text-decoration:none;
        }
        .button:hover {
        	background:linear-gradient(to bottom, #757575 5%, #e6e6e6 100%);
        	background-color:#757575;
        }
        .button:active {
        	position:relative;
        	top:1px;
        }
        </style>
    </head>
    <header>
    <span id="help" style="display:none">
        <h1>Move the download into the same folder as the images.</h1>
        <ul>
        <li>Keep them together.</li>
        <li>If you share the gallery, zip up images along with it.</li>
        <li>Otherwise, they will show up as broken links.</li>
        </ul>
        <a class="button" onClick="this.parentElement.style.display='none'" href="">Okay. Got it.</a>
    </span>
    <label for="ai" style="position:absolute; left:5px; top: 5px;">AI to use 
        <select id="ai" onChange="switch_ai(this.value)">
            <option value="lorem">Lorem Ipsum</option>
            <option value="openai">OpenAI</option>
            <option value="gemini">Gemini</option>
        {% for model in models %}
            <option value="{{ model }}">{{ model }}</option>
        {% endfor %}
        </select>
    </label>
    <div>
        <input class="search" placeholder="Search..." type="search" id="search">
        <svg role="presentation" class="i-search" viewBox="0 0 32 32" width="24" height="24"
    fill="none" stroke="#888" stroke-linecap="round" stroke-linejoin="round" stroke-width="3">
          <circle cx="14" cy="14" r="12" />
          <path d="M23 23 L30 30" />
        </svg>
    <a class="button" id="download">Save Gallery</a></div>
    <a style="position:absolute; right:5px; top:5px;" href="https://github.com/themanyone/FindAImage">FindAImage</a>
    </header>
        {% for image in images %}
            <figure style="float: left; margin: 10px;">
                <img src="{{ url_for('image_file', filename=image) }}" alt="{{ image }}" style="width: 320px;"><br>
                <figcaption onClick="blank(this)" contenteditable="true" id="{{ image.replace('.', '_') }}">{{ figures.get(image, "Click to add searchable caption...") }}</figcaption>
            <a class="button" onclick="describeImage('{{ image }}')">Use AI</a></figure>
        {% endfor %}
    <script>
        function switch_ai(val) {
            //console.log(val);
            fetch('/model/' + val)
        }
        switch_ai(document.getElementById('ai').value);
        function describeImage(imageName) {
            success = false;
            ele = document.getElementById(imageName.replace('.', '_'))
            ele.nextElementSibling.innerText='Please Wait...'
            window.setTimeout(()=>{if(!success){
                ele.nextElementSibling.innerText='Try Again';
            }}, 20000);
            fetch('/describe/' + imageName)
                .then(response => response.json())
                .then(data => {
                    ele.textContent = data.description;
                    success = true;
                    ele.nextElementSibling.innerText='Re-Caption This Image'
                });
        }
        function blank(e){
            if (e.innerHTML=="Click to add searchable caption..."){
                e.innerHTML = "";
            }
        }
        function remove(e){
            let parentNode = e.parentNode;
                parentNode.removeChild(e);
        }
        // Download the finished gallery page
        document.getElementById('download').addEventListener('click', function() {

            // Parse document's HTML
            htmlContent = document.documentElement.outerHTML;
            let parser = new DOMParser();
            doc = parser.parseFromString(htmlContent, 'text/html');

            // Remove links
            doc.querySelectorAll('a').forEach(e=>remove(e));
            // Remove AI dropdown
            remove(doc.querySelector('label[for=ai]'));
            // Remove this script
            remove(doc.querySelector('script'));
            // Remove help span
            remove(doc.querySelector('span'));

            htmlContent = doc.documentElement.outerHTML;

            // Fix quirks mode. Remove /images/ portion of tag
            htmlContent = "<!DOCTYPE html>"+htmlContent.replace(/[/]images[/]/g, "");

            // Create a Blob from the HTML content
            var blob = new Blob([htmlContent], { type: 'text/html' });

            // Create a link element
            var link = document.createElement('a');
            var url = URL.createObjectURL(blob);
            link.href = url;
            link.download = 'index.html';
            link.style.display = 'none';

            // Append link to body, click it, and remove it
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);

            // Show help message
            document.getElementById("help").style.display="inline-block";
        });
        </script><script>
        // Search functions
        let figures = document.querySelectorAll('figure');

        function init() {
            let search = document.getElementById('search');
            search.addEventListener('keyup', filterFigures, true);
            search.addEventListener('click', (e) => {
                e.target.select();
                filterFigures(e);
            }, true);
        }

        function filterFigures(event) {
            if (event.key == "Escape") event.target.value = '';
            let searchTerm = event.target.value.trim().toLowerCase();
            if (searchTerm.length == 0) searchTerm = ' ';
            figures.forEach(figure => {
                if (!figure.querySelector('figcaption')) {
                    //console.log(figure.querySelector('img').src);
                    figure.style.display = 'inline-block';
                } else
                if (figure.querySelector('figcaption').innerText.toLowerCase()
                    .includes(searchTerm))
                    figure.style.display = 'inline-block';
                else figure.style.display = 'none';
            });
        }
        init();
    </script>
    ''', images=image_files, figures=figures_collection, models=models)

@app.route('/model/<ai>')
def model_switch(ai):
    global ai_model
    ai_model = ai
    print("AI model switched to " + ai_model)
    return ai

@app.route('/describe/<filename>')
def describe_image(filename):
    print(f"Generating caption with {ai_model} model")
    if ai_model == 'lorem':
        return jsonify({"description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus. Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor."})

    image_path = os.path.join(IMAGE_FOLDER, filename);
    prompt = "Describe this image in 10-50 words."
    if GEMINI_API_KEY and ai_model == 'gemini':
        # temporarily uploads the image to google
        myfile = genai.upload_file(image_path)
        model = genai.GenerativeModel("gemini-1.5-flash")
        try:
            result = model.generate_content(
                [myfile, "\n\n", prompt]
            )
            return jsonify({"description": f"{result.text}"})
        except ValueError as ve:
            return jsonify({"description": f"{ve}"})
    elif ai_model in models:
        global lclient
        pic = Image.open(image_path)
        image = pic.resize((250, 250))
        # Convert the image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        # Create the data URL
        image_url = f"data:image/png;base64,{image_base64}"

        response = lclient.chat.completions.create(
            model = ai_model,
            messages=[
               {"role": "user", "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            },
                        },
                        {"type": "text", "text": prompt},
                    ]}
            ], stream=False,
            stop=["<|im_end|>", "###"]
        )
        return jsonify({"description": response.choices[0].message.content})
    elif ai_model == 'openai' and gpt_key:
        # FIXME: This OpenAI code might not work, & subscription expired
        # Upload the image to OpenAI
        global client
        with open(image_path, "rb") as image_file:
            file_response = client.files.create(file=image_file,
            purpose='vision')
        file_id = file_response.id

        # Generate caption with GPT-3.5-Turbo
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt} Re. image with file ID: {file_id}" 
                }
            ]
        )
        description = response.choices[0].message.content
        return jsonify({"description": description})
    return jsonify({"description": "no response"})

@app.route('/images/<filename>')
def image_file(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

if __name__ == '__main__':
    host = "http://localhost"
    port = 9165
    print(f"Starting server on {host}:{port}")
    if len(sys.argv) >= 2:
        IMAGE_FOLDER = sys.argv[1]
    else:
        IMAGE_FOLDER = '.'
    print(f"Image folder is {IMAGE_FOLDER}")
#    webbrowser.open(f"{host}:{port}")
    app.run(debug=True, port=port)
