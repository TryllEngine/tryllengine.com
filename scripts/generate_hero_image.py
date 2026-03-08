#!/usr/bin/env python3
"""Generate a hero image for a Tryll Engine blog post using DALL-E 3.

Usage:
    python generate_hero_image.py --prompt "Your DALL-E prompt" --output "assets/blog/my-image.png"
    python generate_hero_image.py --prompt "Your DALL-E prompt" --output "assets/blog/my-image.png" --api-key "sk-..."

The script looks for OPENAI_API_KEY in:
1. --api-key argument
2. .env file in the current directory
3. .env file in the project root (parent directories)
4. OPENAI_API_KEY environment variable
"""

import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path


def find_env_file():
    """Search for .env file in current and parent directories."""
    current = Path.cwd()
    for directory in [current] + list(current.parents):
        env_path = directory / ".env"
        if env_path.exists():
            return env_path
    return None


def load_api_key(cli_key=None):
    """Load OpenAI API key from available sources."""
    # 1. CLI argument
    if cli_key:
        return cli_key

    # 2. .env file
    env_path = find_env_file()
    if env_path:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("OPENAI_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip("'\"")
                    if key:
                        return key

    # 3. Environment variable
    key = os.environ.get("OPENAI_API_KEY")
    if key:
        return key

    return None


def generate_image(prompt, api_key, output_path):
    """Call DALL-E 3 API and save the result."""
    url = "https://api.openai.com/v1/images/generations"

    payload = json.dumps({
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
        "quality": "standard",
        "response_format": "b64_json"
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

    try:
        print(f"Generating image with DALL-E 3...")
        with urllib.request.urlopen(req, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"API error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)

    # Decode, resize to 512x512, and save
    b64_data = data["data"][0]["b64_json"]
    image_bytes = base64.b64decode(b64_data)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    # Resize from 1024x1024 to 512x512 to keep file size reasonable (~300-400 KB)
    try:
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(image_bytes))
        img = img.resize((512, 512), Image.LANCZOS)
        img.save(output, "PNG", optimize=True)
    except ImportError:
        # Fallback: save full-size if Pillow not available
        output.write_bytes(image_bytes)
        print("Warning: Pillow not installed, saved full 1024x1024 image. Run 'pip install Pillow' for auto-resize.")

    revised_prompt = data["data"][0].get("revised_prompt", "")
    print(f"Image saved to: {output}")
    if revised_prompt:
        print(f"DALL-E revised prompt: {revised_prompt}")

    return str(output)


def main():
    parser = argparse.ArgumentParser(description="Generate blog hero image via DALL-E 3")
    parser.add_argument("--prompt", required=True, help="DALL-E prompt for the image")
    parser.add_argument("--output", required=True, help="Output file path (e.g., assets/blog/my-post.png)")
    parser.add_argument("--api-key", help="OpenAI API key (optional, reads from .env if not provided)")
    args = parser.parse_args()

    api_key = load_api_key(args.api_key)
    if not api_key:
        print("Error: No OpenAI API key found.", file=sys.stderr)
        print("Provide it via --api-key, OPENAI_API_KEY in .env, or environment variable.", file=sys.stderr)
        sys.exit(1)

    generate_image(args.prompt, api_key, args.output)


if __name__ == "__main__":
    main()
