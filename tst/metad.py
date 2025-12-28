#!/usr/bin/python
import sys
from PIL import Image, ExifTags

def read_image_metadata(image_path):
    try:
        # Open the image using Pillow
        with Image.open(image_path) as img:
            print(f"Image File: {image_path}")
            print(f"Format: {img.format}")
            print(f"Size: {img.size}")
            print(f"Mode: {img.mode}")

            # Try to extract EXIF data
            exif_data = img.getexif()
            if exif_data:
                print("EXIF Data:")
                for tag_id in exif_data:
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    data = exif_data.get(tag_id)
                    # Some tags might contain nested data, so we handle them
                    if isinstance(data, bytes):
                        data = data.decode('utf-8', 'ignore')
                    print(f"  {tag}: {data}")
            else:
                print("No EXIF data found.")
    except Exception as e:
        print(f"Error reading image metadata: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python read_image_metadata.py <image_file>")
        sys.exit(1)

    image_path = sys.argv[1]
    read_image_metadata(image_path)

