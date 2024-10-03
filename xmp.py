#!/usr/bin/python
import sys
import os
import exiftool

def get_keywords(image_path):
    try:
        with exiftool.ExifToolHelper() as et:
            metadata = et.get_metadata(image_path)[0]
            for key, value in metadata.items():
                if key.startswith("XMP") and "Subject" in key:
                    return str.join(' ', value)

    except Exception as e:
        print(f"Error: {str(e)}")

def get_custom_metadata(image_path):
    try:
        with exiftool.ExifToolHelper() as et:
            metadata = et.get_metadata(image_path)[0]

            print(f"Custom metadata for image: {image_path}\n")

            # Look for common namespaces that might contain custom data
            custom_namespaces = ['XMP', 'IPTC', 'MWG']

            custom_fields_found = False
            for key, value in metadata.items():
                # Check if the key starts with any of the custom namespaces
                if any(key.startswith(ns) for ns in custom_namespaces):
                    print(f"{key}: {value}")
                    custom_fields_found = True

            if not custom_fields_found:
                print("No custom fields found in the standard namespaces.")

            # You can also print all metadata if needed
            print("\nAll metadata fields:")
            for key, value in metadata.items():
                print(f"{key}: {value}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    if not os.path.exists(image_path):
        print(f"Error: The file {image_path} does not exist.")
        sys.exit(1)

#    get_custom_metadata(image_path)
    print(get_keywords(image_path))
