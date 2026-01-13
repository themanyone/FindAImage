#!/usr/bin/env python3
import csv
from huggingface_hub import HfApi

def generate_gguf_multimodal_csv(output_file="models.csv"):
    api = HfApi()

    # Target tasks and the 'gguf' library filter
    categories = [
        "audio-text-to-text",
        "image-text-to-text",
        "video-text-to-text",
        "any-to-any"
    ]

    category_data = {}
    models = []
    for tag in categories:
        models += api.list_models(
            filter=tag,
            sort="downloads",
            direction=-1,
            limit=5000
        )

    # Write to CSV
    with open(output_file, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Model ID", "Tags"])
        for model in models:
            writer.writerow([model.id,
            [t.split('-')[0] for t in model.tags
            if 'text-to-text' in t or 'any-to-any' in t]])

    print(f"Successfully generated {output_file}.")

if __name__ == "__main__":
    # Install requirement: pip install huggingface_hub
    generate_gguf_multimodal_csv()
