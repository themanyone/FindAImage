#!/usr/bin/python
import os
from bs4 import BeautifulSoup

def parse_html(file_path):
    # Load the HTML file
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    # Dictionary to store the figures with alt text as keys
    figures_dict = {}
    # Find all <figure> elements
    figures = soup.find_all('figure')

    for figure in figures:
        # Find the <img> tag within the <figure>
        img_tag = figure.find('img')
        if img_tag and img_tag.has_attr('alt'):
            # assuming alt is image name
            alt_text = img_tag['alt']
            # Store the figure element in the dictionary
            caption = figure.find('figcaption')
            txt = str(caption.contents[0])
            figures_dict[alt_text] = txt

    return figures_dict

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_index.html>")
        sys.exit(1)

    index_path = sys.argv[1]

    if not os.path.exists(image_path):
        print(f"Error: The index.html at {image_path} does not exist.")
        sys.exit(1)

    print(parse_html(index_path))
