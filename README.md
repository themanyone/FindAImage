# FindAImage

Using AI image descriptions to organize memes.

Who doesn't have a folder of their favorite memes? But it becomes tedious scrolling through pages and pages of memes to find the right one for every occasion.

Now that AI can describe photos, the first idea was to create a searchable database to store the memes, along with their descriptions. But the the pictures already exist inside a folder. Isn't that some sort of database already? The next idea was to add metadata to the images. But the metadata isn't searchable except by using tools like `grep` from the command line. And it modifies the files. We don't want to do that.

What was needed was a way to display images with captions that could be easily searched by typing a few words. And the best way to do that is using a browser.

![preview](preview.png)

## Get updates from GitHub

```bash
git clone https://github.com/themanyone/FindAImage.git
cd FindAImage
```

Or, if it's already downloaded, `git pull`.

## Install dependencies

Install at least tidy. If you need documentation, consider also installing `pinfo`.

Fedora, Centos.
`dnf install tidy pinfo`

Ubuntu, Debian.
`dpkg -i tidy pinfo`

Arch
`pacman -S tidy pinfo`

## Install [llama.cpp](https://github.com/themanyone/llama.cpp.git)

For this project, we are using our own unofficial fork of [llama.cpp](https://github.com/themanyone/llama.cpp.git). We have submitted our changes via pull request. If accepted, maybe the official version will become usable.

```bash
git clone https://github.com/themanyone/llama.cpp.git
git checkout hk # switch to --template branch.
```

Build according to the project's instructions.

Install by copying executables to somewhere in $PATH, such as `~/.local/bin/`.

`cp llama-* ~/.local/bin/`

Link the models directory.

```bash
cd #llama.cpp
ln -s $(pwd)/models ~/.local/share/models
```

Obtain a [llava model](https://huggingface.co/xtuner/llava-phi-3-mini-gguf/tree/main) and matching `mmproj` file from huggingface in `gguf` format.

```bash
wget -c https://huggingface.co/xtuner/llava-phi-3-mini-gguf/resolve/main/llava-phi-3-mini-int4.gguf?download=true
wget https://huggingface.co/xtuner/llava-phi-3-mini-gguf/resolve/main/llava-phi-3-mini-mmproj-f16.gguf?download=true
```

## Build scripts

Create a script to launch the llava model and mmproj file together with your favorite options. Running this command will recreate `~/.local/bin/llava_phi3.sh`. But maybe you should edit this in case locations are different.

```bash
cat << EOF > ~/.local/bin/llava_phi3.sh
llama-llava-cli -ngl 16 \
-m ~/.local/share/models/llava-phi-3-mini-int4.gguf \
--mmproj  ~/.local/share/models/llava-phi-3-mini-mmproj-f16.gguf \
-c 4096 "$@"
EOF
```

Now we are ready to test the model on some images. First, try a single image. Change directory to where images reside.

```bash
cd ~/Pictures
llava_phi3.sh --image file.jpg
```

## Gather image data

If that works, we can create a database in the form of a web page of the whole directory. While technically not a database, it allows visual and text searching, plus copy and paste access to photographs.

```bash
shopt -s nullglob
printf -- "--image %q " *.png *.webm *.jpg *.jpeg|xargs llava_phi3.sh -p "Write a quick, 10-50 word caption for this image. Just one caption. Minimum 10 words." --template '<figure><img src="[image]" alt="[[image]]"><figcaption>[description]</figcaption></figure>' -c 4096 --log-disable | tee data
```

The `printf` `--` option tells printf not to interpret everything as options. The `%q` outputs file names with spaces and special characters properly escaped. We could have used `find` for this. The `nullglob` option to `shopt` is necessary to prevent bash from causing errors if no images are found matching [pattern]. Bash tries to pass off the glob pattern itself as one of the images. So we turn that feature off. 

You can even recurse subdirectories with `printf`, if you enable globstar `shopt -s globstar`. For more information (FYI): `pinfo bash --node "The Shopt Builtin"`.

### Update from .csv

Someday you might want to update the captions, working with a subset of images in a comma-separated, quoted `.csv` file. This is made possible by reading the data into an array. FYI: `pinfo bash --node "Arrays"`

`IFS="," read -r -a a <<< "files.csv"`

Or if you have `xsel` installed. You can work with .csv data copied to the clipboard with `CTRL-C`.

`IFS="," read -r -a a <<< "$(xsel -b)"`

The `IFS` file seperator tells Bash the file is comma-separated. FYI: `pinfo bash --node "Word Splitting"`

```
echo "${a[@]}"|xargs printf -- "--image %q " | xargs llava_phi3.sh -p "Write a quick, 10-50 word caption for this image. Just one caption. Minimum 10 words." --template '<figure><img src="[image]" alt="[[image]]"><figcaption>[description]</figcaption></figure>' -c 4096 --log-disable | tee data
```

The `echo "${a[@]}"` echos the file names properly quoted. FYI: pinfo bash --node "Quoting". We use `xargs` repeatedly to keep file name arguments quoted as they pass through the pipeline.

## Analyze image data

Photos are processed one by one, formatting the output according to the
template we provided. We now have a data file that looks like this.

```
<figure><img src="test pattern.png" alt="test pattern.png"><figcaption> The colorful television screen displays the image of a fish tank with blue, red, yellow, green, and blue elements.

</figcaption></figure><figure><img src="trading patterns.png" alt="trading patterns.png"><figcaption> A computer monitor displaying a variety of graphs and diagrams.

</figcaption></figure><figure><img src="Youtube-button.png" alt="Youtube-button.png"><figcaption> The YouTube logo is red and white.

</figcaption></figure><figure><img src="20230218_215924.jpg" alt="20230218_215924.jpg"><figcaption> A small digital scale shows the number 378.

</figcaption></figure><figure><img src="dad.jpg" alt="dad.jpg"><figcaption> A person plays the grand piano in an exhibition hall.

</figcaption></figure><figure><img src="ferry.jpg" alt="ferry.jpg"><figcaption> A boat is docked at a port near a forest.

</figcaption></figure><figure><img src="github_error.jpg" alt="github_error.jpg"><figcaption> The image shows a screenshot of a screenshot of a screenshot of a screenshot of a screenshot of a screenshot of a screenshot of a screenshot of a screenshot</figcaption></figure>
```

## Build a web page automatically

We could manually clean this `data` up to make a proper HTML page. But tools like HTML tidy already exist for that. This command builds `album.html` from `data`.

`tidy -i -o album.html data`

```
<!DOCTYPE html>
<html>
<head>
  <meta name="generator" content=
  "HTML Tidy for HTML5 for Linux version 5.8.0">
  <title></title>
</head>
<body>
  <figure>
    <img src="test%20pattern.png" alt="test pattern.png">
    <figcaption>
      The colorful television screen displays the image of a fish
      tank with blue, red, yellow, green, and blue elements.
    </figcaption>
  </figure>
  <figure>
    <img src="trading%20patterns.png" alt="trading patterns.png">
    <figcaption>
      A computer monitor displaying a variety of graphs and
      diagrams.
    </figcaption>
  </figure>
...
```

We now have a nice web page of photos with AI-generated captions. Feel free to make corrections. Let's add some CSS to make the photo album look better. Insert `<link rel="stylesheet" href="album.css">` somewhere between the <head> and </head> tags.

```
<!DOCTYPE html>
<html>
<head> 
  <meta name="generator" content=
  "HTML Tidy for HTML5 for Linux version 5.8.0">
  <title></title>
  <link rel="stylesheet" href="album.css">
</head>
...
```

And create a basic css file.

```
cat << EOF > album.css
  img{
    height:300px;
  }
  figure{
    width:350px;
    display:inline-block;
    white-space: nowrap;
  }
  figcaption {
    position: absolute;
    width: inherit;
    overflow: hidden;
    text-overflow: ellipsis;
    background: #181818;
  }
  figure:hover{
    white-space: normal;
  }
  body{
    background-color: #181818;
    color: #e0e0e0;
  }
EOF
```

Launch the album in the default web browser. 

`xdg-open album.html`

Search for text captions in the browser by pressing `CTRL+F`. It will scroll to the image in question. Right click on your mug shots to copy them, paste them to social media, etc. You could also publish the album on a web server, [github pages](https://pages.github.com/), or [google drive](https://dev.to/matinmollapur0101/how-to-use-google-drive-to-host-your-website-1oen). Or good old-fashioned `lftp` to your server box.

## Advanced usage

Some javascript has been added to alternately show and hide groups of images based on what you type into a search bar. For an example of this, look in the `memes` directory. You may use this so long as it doesn't become a hidden part of a commercial product.

## Closing thoughts

Well, that's it. We built `llama.cpp`, downloaded a llava model, made some scripts, and built a static web page with AI-generated image captions. What else could we be doing with the help of AI?

## Discuss

    - GitHub https://github.com/themanyone
    - YouTube https://www.youtube.com/themanyone
    - Mastodon https://mastodon.social/@themanyone
    - Linkedin https://www.linkedin.com/in/henry-kroll-iii-93860426/
    - [TheNerdShow.com](http://thenerdshow.com/)

Copyright (C) 2024 Henry Kroll III, www.thenerdshow.com. See [LICENSE](LICENSE) for details.
