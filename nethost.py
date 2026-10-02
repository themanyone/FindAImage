#!/usr/bin/env python
"""Module: nethost
Description: Shared networking helpers for the FindAImage apps. Resolves the
model server endpoint (from the LLAVA_ENDPOINT environment variable), builds
OpenAI clients pointed at it, probes ports, and fetches the model list with
retries so a freshly-started llama-server is not missed.

License: Copyright (C) 2026 Henry F Kroll III, see LICENSE
"""
import os
import socket
import time
from urllib.parse import urlparse


def endpoint():
    """Module: endpoint
    :returns: (base URL, port) of the model server"""
    url = os.environ.get("LLAVA_ENDPOINT", "http://localhost:8087/v1")
    return url, urlparse(url).port or 8087


if "LLAVA_ENDPOINT" not in os.environ:
    print(f"Using default model server at {endpoint()[0]}. "
          "Export LLAVA_ENDPOINT to change it.")


def hint():
    """Module: hint
    :returns: Message explaining how to start the model server"""
    url, port = endpoint()
    return (
        f"\nNo model server found at {url}.\n"
        f"Start llama-server with a multimodal model on the port matching that endpoint, e.g.:\n"
        f"  llama-server -ngl 16 -hf unsloth/Qwen2.5-VL-3B-Instruct-GGUF:IQ4_NL --port {port} -n 200 -a \"Qwen2.5-vision\"\n"
        f"The -a flag names the model's capabilities (\"vision\", \"audio\", or \"omni\").\n"
        f"To point these apps at another server, export LLAVA_ENDPOINT=\"http://localhost:PORT/v1\"\n"
    )


def get_client(api_key="llama.cpp", timeout=30):
    """Module: get_client
    :param api_key: (dummy) key for the local model server
    :param timeout: request timeout in seconds
    :returns: OpenAI client pointed at the model server"""
    from openai import OpenAI
    return OpenAI(base_url=endpoint()[0], api_key=api_key, timeout=timeout)


def port_free(port, host="0.0.0.0"):
    """Module: port_free
    :param port: TCP port to probe
    :param host: interface to bind on
    :returns: True when nothing is listening on the port"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False


def fetch_models(retries=5, delay=2):
    """Module: fetch_models
    :param retries: number of attempts before giving up
    :param delay: seconds to wait between attempts
    :returns: list of model IDs, retries while llama-server starts up"""
    client = get_client()
    for n in range(retries):
        try:
            return [m.id for m in client.models.list()]
        except Exception:
            if n == retries - 1:
                raise
            time.sleep(delay)