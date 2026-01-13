#!/usr/bin/env python3
import sys
import ast
import csv
import argparse

def get_caps(lookup):
    try:
        with open('models.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if lookup in row['Model ID'].lower():
                    s = row['Tags']
                    try:
                        tags = ast.literal_eval(s)
                    except (ValueError, SyntaxError):
                        print("Error parsing tags.")
                        tags = []
                    return tags
    except FileNotFoundError:
        print("CSV file not found. Run update_models.py to generate it.")
    return []

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('model_id', type=str, help='Model ID to look up')
    args = parser.parse_args()
    tags = get_caps(args.model_id.lower().split(':')[0])
    print(f"tags: {tags}")

if __name__ == '__main__':
    main()
