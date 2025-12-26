#!/usr/bin/python
"""Module: AI Image Gallery
Description: Create searchable photo albums and online image portfolios
with the help of AI.
License: Copyright (C) 2024 Henry F Kroll III, see LICENSE
"""
import io
import os
import sys
import base64
from PIL import Image
from flask import Flask, send_from_directory, render_template_string, jsonify
import google.generativeai as genai
from openai import OpenAI
from figs import parse_html
from xmp import get_keywords

client = OpenAI()
app = Flask(__name__)
IMAGE_FOLDER="."
app.model = 'lorem' # default to lorem ipsum
# Local llava-llama.cpp endpoint
LLAVA_ENDPOINT = "http://localhost:8087/v1"
lclient = OpenAI(base_url=LLAVA_ENDPOINT, api_key="sk-xxx")
# Discover llava/vision/omni models to show in dropdown box (case-insensitive)
models = [model.id for model in lclient.models.list()
    if any(k in model.id.lower() for k in ("llava", "vision", "omni"))]
# Lowercase set for case-insensitive checks
models_lower = {m.lower() for m in models}
# Google Gemini API endpoint
GEMINI_API_ENDPOINT = "https://api.gemini.google/v1/text"
# Your Gemini API key (export GENAI_TOKEN)
GEMINI_API_KEY = os.environ.get("GENAI_TOKEN")
genai.configure(api_key=GEMINI_API_KEY)
# Configure OpenAI
gpt_key = os.getenv("OPENAI_API_KEY")
OpenAI.api_key = gpt_key

@app.route('/')
def gallery():
    """Module: gallery: Generate the portfolio builder page
    
    :inputs: None
    :outputs: None"""
    # Fill collection with existing captions / EXIF XMP keywords
    figures_collection = {}
    # Get captions (figures_collection) from index.html, if it exists
    index_path = os.path.join(IMAGE_FOLDER, 'index.html')
    image_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    audio_files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a'))]
    if os.path.isfile(index_path):
        figures_collection = parse_html(index_path)
    else:
        # Populate captions / keywords for both images and audio files
        for fname in image_files + audio_files:
            figures_collection[fname] = get_keywords(os.path.join(IMAGE_FOLDER, fname))
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
        .waveform {
            display: block;
            width: 320px;
            height: 64px;
            background: #222;
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
    <!-- AI Caption All: caption all visible media using the selected AI model -->
    <a class="button" id="ai_caption_all" title="Caption all media on this page using AI">AI Caption All</a>
    <a class="button" id="download">Save Gallery</a></div>
    <a style="position:absolute; right:5px; top:5px;" href="https://github.com/themanyone/FindAImage">FindAImage</a>
    </header>
        {% for image in images %}
            <figure style="float: left; margin: 10px;" title="{{ image }}">
                <img src="{{ url_for('image_file', filename=image) }}" alt="{{ image }}" title="{{ image }}" style="width: 320px;"><br>
                <figcaption onClick="blank(this)" contenteditable="true" id="{{ image.replace('.', '_') }}">{{ figures.get(image, "Click to add searchable caption...") }}</figcaption>
            <a class="button ai-button" data-type="image" data-filename="{{ image }}" onclick="describeImage('{{ image }}')">Use AI</a></figure>
        {% endfor %}
        {% for audio in audios %}
            <figure style="float: left; margin: 10px;" title="{{ audio }}">
                <audio id="audio_{{ audio.replace('.', '_') }}" controls src="{{ url_for('media_file', filename=audio) }}" title="{{ audio }}" style="width: 320px;"></audio><br>
                <canvas class="waveform" id="wave_{{ audio.replace('.', '_') }}" data-src="{{ url_for('media_file', filename=audio) }}" title="{{ audio }}" width="320" height="64"></canvas>
                 <figcaption onClick="blank(this)" contenteditable="true" id="{{ audio.replace('.', '_') }}">{{ figures.get(audio, "Click to add searchable caption...") }}</figcaption>
                 <!-- Use AI button for audio (hidden by default, shown for Omni models) -->
                 <a class="button ai-audio ai-button" data-type="audio" data-filename="{{ audio }}" style="display:none" onclick="describeAudio('{{ audio }}')">Use AI</a>
             </figure>
         {% endfor %}
    <script>
        function switch_ai(val) {
            //console.log(val);
            fetch('/model/' + val)
            // Show audio AI buttons only when Omni model is selected
            const showAudioAI = (val || '').toLowerCase().includes('omni');
            document.querySelectorAll('.ai-audio').forEach(b => b.style.display = showAudioAI ? 'inline-block' : 'none');
        }
        switch_ai(document.getElementById('ai').value);
        function describeImage(imageName) {
            let success = false;
            const ele = document.getElementById(imageName.replace('.', '_'));
            const btn = ele ? ele.nextElementSibling : null;
            if (btn) btn.innerText = 'Please Wait...';
            const to = setTimeout(()=>{ if(!success && btn) btn.innerText = 'Try Again'; }, 20000);
            return fetch('/describe/' + imageName)
                .then(response => response.json())
                .then(data => {
                    if (ele) ele.textContent = data.description;
                    success = true;
                    if (btn) btn.innerText = 'Re-Caption This Image';
                    clearTimeout(to);
                    return data;
                })
                .catch(err => {
                    if (btn) btn.innerText = 'Error';
                    clearTimeout(to);
                    throw err;
                });
        }
        function describeAudio(audioName) {
            let success = false;
            const ele = document.getElementById(audioName.replace('.', '_'));
            const btn = ele ? ele.nextElementSibling : null;
            if (btn) btn.innerText = 'Please Wait...';
            const to = setTimeout(()=>{ if(!success && btn) btn.innerText = 'Try Again'; }, 20000);
            return fetch('/describe/' + audioName)
                .then(response => response.json())
                .then(data => {
                    if (ele) ele.textContent = data.description;
                    success = true;
                    if (btn) btn.innerText = 'Re-Caption This Audio';
                    clearTimeout(to);
                    return data;
                })
                .catch(err => {
                    if (btn) btn.innerText = 'Error';
                    clearTimeout(to);
                    throw err;
                });
        }
        // Caption all visible media sequentially using currently selected AI
        async function aiCaptionAll() {
            const control = document.getElementById('ai_caption_all');
            if (!control) return;
            const original = control.innerText;
            control.disabled = true;
            control.innerText = 'Captioning...';
            const items = Array.from(document.querySelectorAll('.ai-button'));
            for (const item of items) {
                // skip hidden buttons
                if (item.offsetParent === null) continue;
                const type = item.dataset.type;
                const fname = item.dataset.filename;
                try {
                    if (type === 'audio') await describeAudio(fname);
                    else await describeImage(fname);
                } catch (e) {
                    console.log('AI caption error', e);
                }
                // small delay between items
                await new Promise(r => setTimeout(r, 500));
            }
            control.innerText = 'Done';
            setTimeout(()=> { control.innerText = original; control.disabled = false; }, 1500);
        }
        document.getElementById('ai_caption_all').addEventListener('click', aiCaptionAll);
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

            // Fix quirks mode. Remove /images/ and /media/ portions of tag for portability
            htmlContent = "<!DOCTYPE html>"+htmlContent.replace(/\\/(images|media)\\//g, "");

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
       
        function filterFigures(event) {
            if (event.key == "Escape") event.target.value = '';
            let searchTerm = (event.target.value || '').trim().toLowerCase();
            if (searchTerm.length == 0) searchTerm = ' ';
            figures.forEach(figure => {
                const caption = figure.querySelector('figcaption');
                if (!caption) {
                    figure.style.display = 'inline-block';
                } else if (caption.innerText.toLowerCase().includes(searchTerm)) {
                    figure.style.display = 'inline-block';
                } else {
                    figure.style.display = 'none';
                }
            });
        }

        function init() {
             let search = document.getElementById('search');
             search.addEventListener('keyup', filterFigures, true);
             search.addEventListener('click', (e) => {
                 e.target.select();
                 filterFigures(e);
             }, true);
            // Draw waveforms for any audio canvases
            document.querySelectorAll('canvas.waveform[data-src]').forEach(c => drawWaveform(c));
         }
 
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        let audioCtx = null;
        async function drawWaveform(canvas) {
            try {
                const url = canvas.dataset.src;
                if (!url) return;
                if (!audioCtx) audioCtx = new AudioCtx();
                const resp = await fetch(url);
                const arrayBuffer = await resp.arrayBuffer();
                const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);
                const raw = audioBuffer.getChannelData(0);
                const w = canvas.width, h = canvas.height;
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#222';
                ctx.fillRect(0, 0, w, h);
                ctx.lineWidth = 1;
                ctx.strokeStyle = '#4CAF50';
                ctx.beginPath();
                const step = Math.max(1, Math.floor(raw.length / w));
                for (let i = 0; i < w; i++) {
                    let min = 1, max = -1;
                    for (let j = 0; j < step; j++) {
                        const v = raw[i * step + j];
                        if (v < min) min = v;
                        if (v > max) max = v;
                    }
                    const x = i;
                    const y1 = (1 + min) * 0.5 * h;
                    const y2 = (1 + max) * 0.5 * h;
                    ctx.moveTo(x, y1);
                    ctx.lineTo(x, y2);
                }
                ctx.stroke();
            } catch (e) {
                console.log('waveform draw error', e);
            }
        }
         init();
     </script>
    ''', images=image_files, figures=figures_collection, models=models
    , audios=audio_files
)

@app.route('/model/<ai>')
def model_switch(ai):
    """Module: model_switch: switch model using dropdown from web page"""
    app.model = ai
    print("AI model switched to " + app.model)
    return ai

@app.route('/describe/<filename>')
def describe_image(filename):
    """Module: describe_image: generate image descriptions
    
    :param filename: name of image file to analyze
    :returns: image description JSON"""
    print(f"Generating caption with {app.model} model")
    if app.model == 'lorem':
        return jsonify({"description":
"Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus. "+
"Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, "+
"dolor."})

    file_path = os.path.join(IMAGE_FOLDER, filename)
    is_audio = filename.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a'))
    prompt = "Describe this audio in 10-50 words." if is_audio else "Describe this image in 10-50 words."

    if GEMINI_API_KEY and app.model.lower() == 'gemini':
        # temporarily uploads the file (image or audio) to google
        myfile = genai.upload_file(file_path)
        model = genai.GenerativeModel("gemini-1.5-flash")
        try:
            response = model.generate_content(
                [myfile, "\n\n", prompt]
            )
            return jsonify({"description": f"{response.text}"})
        except ValueError as ve:
            return jsonify({"description": f"{ve}"})
    elif app.model.lower() in models_lower:
        # For audio files, encode raw bytes into input_audio content (base64 + format).
        if is_audio:
            with open(file_path, "rb") as f:
                audio_bytes = f.read()
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            audio_format = filename.rsplit('.', 1)[1].lower()
            response = lclient.chat.completions.create(
                model=app.model,
                messages=[
                    {"role": "user", "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {
                                "data": audio_base64,
                                "format": audio_format
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]}
                ], stream=False,
                stop=["<|im_end|>", "###"]
            )
            return jsonify({"description": response.choices[0].message.content})
        else:
            # Image path: keep previous behavior
            image = Image.open(file_path).resize((250, 250))
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            image_url = f"data:image/png;base64,{image_base64}"
            response = lclient.chat.completions.create(
                model=app.model,
                messages=[
                   {"role": "user", "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url},
                            },
                            {"type": "text", "text": prompt},
                        ]}
                ], stream=False,
                stop=["<|im_end|>", "###"]
            )
            return jsonify({"description": response.choices[0].message.content})
    elif app.model.lower() == 'openai' and gpt_key:
        if is_audio:
            # OpenAI chat/file handling for audio is not implemented here
            return jsonify({"description": "OpenAI audio analysis is not supported by this gallery interface."})
        # Upload the image to OpenAI
        with open(file_path, "rb") as image:
            file_response = client.files.create(file=image, purpose='vision')
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
        return jsonify({"description": response.choices[0].message.content})
    return jsonify({"description": "no response"})

@app.route('/images/<filename>')
def image_file(filename):
    """Module: image_file: Retrieve local image from flask"""
    return send_from_directory(IMAGE_FOLDER, filename)

@app.route('/media/<filename>')
def media_file(filename):
    """Serve audio/media files from the gallery folder"""
    return send_from_directory(IMAGE_FOLDER, filename)

if __name__ == '__main__':
    HOST = "http://localhost"
    PORT = 9165
    print(f"Starting server on {HOST}:{PORT}")
    if len(sys.argv) >= 2:
        IMAGE_FOLDER = sys.argv[1]
    else:
        IMAGE_FOLDER = '.'
    print(f"Image folder is {IMAGE_FOLDER}")
#    webbrowser.open(f"{host}:{port}")
    app.run(debug=True, port=PORT)
