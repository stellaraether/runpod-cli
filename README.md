# RunPod CLI

Command line interface for RunPod serverless endpoints.

## Installation

```bash
pip install runpod-cli
```

## Setup

Configure your RunPod API key:

```bash
runpod configure
```

Or with the flag:

```bash
runpod configure --api-key your-api-key
```

## Usage

### Image Editing

Edit images using the `google-nano-banana-2-edit` endpoint:

```bash
# Edit a single image
runpod image edit -p "make the person smile" -i https://example.com/photo.jpg

# Edit with multiple reference images
runpod image edit -p "combine these into a collage" -i https://example.com/a.jpg -i https://example.com/b.jpg

# Save result to file
runpod image edit -p "add a sunset background" -i https://example.com/photo.jpg -o result.json
```

### Video Generation

Generate video from an image using the `google-veo3-1-fast-i2v` endpoint:

```bash
# Generate video from image
runpod video generate -p "a cat walking in a garden" -i https://example.com/cat.jpg

# Save result to file
runpod video generate -p "camera panning across the landscape" -i https://example.com/scene.jpg -o video.json
```

### Async Jobs

For long-running tasks, use async job management:

```bash
# Submit an async job
runpod job submit my-endpoint-id '{"prompt": "hello"}'

# Check job status
runpod job status my-endpoint-id <job-id>

# Cancel a job
runpod job cancel my-endpoint-id <job-id>
```

### Raw Input

Pass raw JSON input to any endpoint:

```bash
runpod image edit --raw-input '{"prompt": "custom", "image_urls": ["https://example.com/img.jpg"]}' --endpoint-id custom-endpoint
```

## Development

```bash
# Clone repo
git clone https://github.com/stellaraether/runpod-cli.git
cd runpod-cli

# Install in editable mode
pip install -e .

# Run locally
python3 -m runpod_cli --help
```

## Requirements

- Python 3.8+
- RunPod API key

## License

MIT
