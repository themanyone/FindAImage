
# FindAImage

Use manually-entered and AI-generated descriptions to build organized photo albums, multimedia portfolios, and meme pages.

 * Simple utility. Creates searchable media captions, in browser.
 * Offline and private. Or optionally use OpenAI or Google.
 * Internet-ready. Can publish album/portfolio as a website.
 * Light wight. Does not require torch. 4GiB VRAM.
 * Free and open-source. NO WARRANTIES. See LICENSE.

![preview](preview.png)

Who doesn't have a folder of their favorite memes? But it becomes tedious scrolling through pages and pages of memes, photos, and audio clips to find the right one for every occasion.

**New Features.**
* Omni support - Generate AI captions for audio files as well as images.
* `aichat.py` server - supports multimodal text, image, and audio input.

Enjoying it so far, or want more features? [Support development.](https://www.paypal.com/donate/?hosted_button_id=A37BWMFG3XXFG) (PayPal donation link).

## Get updates from GitHub

```bash
git clone https://github.com/themanyone/FindAImage.git
cd FindAImage
```

Or, if it's already downloaded, `git pull`.

## Python Dependencies

To keep requirements from potentially messing up your default python setup, and to speed things up, you might want to install and use `uv` to create a virtual environment.

```shell
sudo dnf -y install uv
uv venv -p python3.13 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Optional ChatGPT from OpenAI

Export `OPENAI_API_KEY` to enable ChatGPT. Edit `.bashrc`, or another startup file to make it permanent.

```shell
export OPENAI_API_KEY=<my API key>
```

## Optional Google Gemini

* Sign up for a [GOOGLE_API_KEY](https://aistudio.google.com)
* `pip install -q -U google-generativeai`
* `export GENAI_KEY=<YOUR API_KEY>`

## Local LLAVA server

A local server is our preferred way to generate captions, avoid censorship, and keep everything private. Let's build a local GPU-accelerated AI model server. 

Build [llama.cpp](https://github.com/ggml-org/llama.cpp) according to their instructions. Compile it with the type of acceleration that supports your hardware, if possible. Prefer CUDA for Nvidia GPU cards.

## Start LLAVA Server

If you have more than 4GB VRAM, you can remove -ngl option to offload all layers to GPU. We are using a different port than normal for this dedicated server. Feel free to change it, and modify the chat clients with the new port.

- Text & image (Download any GGUF. We are using IQ4_NL quantized model, about 3GiB).
- We use -a "model-alias" with "llava", "vision", "vox" or "omni" to tell our program to use those capabilities. 
- We also limit token generation to 200 to prevent these models from running on and overheating.

**Vision/LLAVA.** Caption your images.

`llama-server -ngl 16 -hf unsloth/Qwen2.5-VL-3B-Instruct-GGUF:IQ4_NL --port 8087 -n 200 -a "Qwen2.5-vision"`

**Text & audio.** Caption audio, not images. (just over 2GiB download).

`llama-server -ngl 17 -hf ggml-org/ultravox-v0_5-llama-3_2-1b-GGUF --port 8087 -n 200 -a "Ultravox"`

**Omni models.** Support both image & audio captions.

`llama-server -ngl 16 -hf ggml-org/Qwen2.5-Omni-3B-GGUF:Q4_K_M --port 8087 -n 200 -a "Qwen2.5-Omni"`

[Multimodal text & video](https://huggingface.co/Mungert/SkyCaptioner-V1-GGUF) (Video may not be supported by llama-server yet but link has good info & scripts).

## Router Mode

If you have several AI models, you might want to try `llama-server`'s [router mode](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md#using-multiple-models), that serves up all the models in your `/models` directory. Then our apps can choose among them.

**Omni model crashes.** If you use llama.cpp's router with Omni model, it crash with a message to the effect that it requires ub >= c. This might not always be the case, but just a FYI. We had to use -ub option or put ub into the configuration in our .models.ini:

```
[Qwen2.5-Omni-7B-IQ4_XS]
ngl = 29
c = 16384
ub = 16384
```

## Our Own Chat Server

`python aichat.py`

This starts a chat server (yes, yet another server--a web server this time) so, if port 7860 is open on your firewall, anyone on your wifi can interact with `llama-server` via our chat app. Upload or capture pictures from a webcam (for models that support them), read and translate text in images, or ask questions about them. Right now, ours is the only chat app, *that we know of*, that can prompt an omni model with text, audio, and images simultaneously. Try speaking your prompt into the recorded audio and see!

**Update.** Now that llama.cpp also has a chat server of their own, you may want to try that. Theirs doesn't record audio or handle multimodal prompts as well as ours yet. But it might later.

**Up/down voting.** Now that `aichat.py`'s up and down-voting works, you can rank which models you like best. The rankings will appear in a file, `votes.json`. If you have downloaded several models, you could use that data later to decide which models to keep.

**Canvas mode.** You can edit questions, code, and responses right in the interface by clicking twice on the text. A button will appear to submit a new query with your edits, comments, or annotations.

![chat](chat.png)

## Photo Album Builder

Test captioning photos in the memes directory. This will launch a server to host the photo album builder. The builder then creates a web page that will be the photo album or media portfolio.

`./album_create.py memes`

You should see a URL for the photo album builder. `Ctrl+click` it to open it. Or type it into your browser. Monitor memory usage with `nvtop`.

The link might look something like this. `http://localhost:9165`

If there is an existing `index.html` in the image folder, it will import captions from there. If not, it will scan the image metadata for keywords. If the photos were already tagged with keywords using a tool like [LLavaImageTagger](https://github.com/jabberjabberjabber/LLavaImageTagger) it will display those. (You must install LLavaImageTagger to make that work).

When Omni model is selected, the photo album builder can also caption audio files!

**Supervise children.** Be aware that these models are under active development. Their output, though usually fine, *may not always be safe* for all ages.

Once you open the link, and see the browser interface,
- select a vision model from the drop-down in the upper-left,
- click buttons to generate captions,
- click inside text boxes to manually edit captions, 
- and save the annotated photo album.

The saved abum will go into your Downloads folder. Move the downloaded `index.html` back into the directory where the images are. Launch it with a browser (or double click it in your file manager) any time you want to search images. Feel free to customize it, add CSS styles, etc.

Now try making albums/portfolios in your other image folders.

```shell
./album_create.py ~/Pictures/2026
```

## Launch the album

Rename the album to something creative. Launch the album in the default web browser. 

`xdg-open album.html`

Create a link to your album on the desktop. While viewing the album, simply drag the link in the address bar to the desktop. Or create a simlink from the command line.

`ln -s album.html ~/Desktop/`

Search for text captions in the browser by pressing `CTRL+F`. It will scroll to the image in question. Right click on your mug shots to copy them, paste them to social media, etc. You could also publish the album on a web server, [github pages](https://pages.github.com/), or [google drive](https://dev.to/matinmollapur0101/how-to-use-google-drive-to-host-your-website-1oen). Or good old-fashioned `lftp` to your server box.

## Advanced search

There is some JavaScript to alternately show and hide groups of images based on what you type into a search bar. For an example of this, look in the `memes` directory. You may use this so long as it doesn't become part of a commercial product that denies proper credit and royalties to the author.

## Closing thoughts

Well, that's it. We built `llama.cpp`, made AI image descriptions locally, and built a photo album. We made a searchable web page, with AI-generated image captions. And we created a shortcut on the Desktop. What else could we be doing with the help of AI?

## Discuss

    - GitHub https://github.com/themanyone
    - YouTube https://www.youtube.com/themanyone
    - Mastodon https://mastodon.social/@themanyone
    - Linkedin https://www.linkedin.com/in/henry-kroll-iii-93860426/
    - Buy me a coffee https://buymeacoffee.com/isreality
    - [TheNerdShow.com](http://thenerdshow.com/)

Copyright (C) 2024-2026 Henry Kroll III, www.thenerdshow.com. See [LICENSE](LICENSE) for details.
