#!/usr/bin/env python3
"""
Test client for RL-TTS service
"""
import requests
import json
import sys

def test_tts(host="localhost", port=8080, text="Hello, this is a test of the text to speech service.", language="en"):
    """Test the TTS service"""
    url = f"http://{host}:{port}/synthesize"

    payload = {
        "text": text,
        "language": language
    }

    print(f"Testing TTS service at {url}")
    print(f"Text: {text}")
    print(f"Language: {language}")

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        result = response.json()
        audio_data = bytes(result['audio_data'])

        print(f"\nSuccess!")
        print(f"Audio length: {len(audio_data)} bytes")
        print(f"Sample rate: {result['sample_rate']} Hz")
        print(f"Format: {result['format']}")

        # Save audio to file
        output_file = "test_output.raw"
        with open(output_file, "wb") as f:
            f.write(audio_data)
        print(f"\nAudio saved to {output_file}")
        print(f"Play with: ffplay -f s16le -ar 8000 -ac 1 {output_file}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        sys.exit(1)


def test_health(host="localhost", port=8080):
    """Test the health endpoint"""
    url = f"http://{host}:{port}/health"

    try:
        response = requests.get(url)
        response.raise_for_status()

        result = response.json()
        print(f"Health check: {json.dumps(result, indent=2)}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test RL-TTS service")
    parser.add_argument("--host", default="localhost", help="Service host")
    parser.add_argument("--port", type=int, default=8080, help="Service port")
    parser.add_argument("--text", default="Hello, this is a test of the text to speech service.", help="Text to synthesize")
    parser.add_argument("--language", default="en", help="Language code (en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh-cn, ja, hu, ko)")
    parser.add_argument("--health", action="store_true", help="Run health check only")

    args = parser.parse_args()

    if args.health:
        test_health(args.host, args.port)
    else:
        test_tts(args.host, args.port, args.text, args.language)

