"""Core CLI infrastructure and shared utilities for RunPod CLI."""

import functools
import json
import sys
from pathlib import Path

import click
import requests

from runpod_cli.client import RunPodClient
from runpod_cli.config import Config

DEFAULT_IMAGE_ENDPOINT = "google-nano-banana-2-edit"
DEFAULT_VIDEO_ENDPOINT = "google-veo3-1-fast-i2v"


def _check_path():
    """Check if the CLI is accessible in PATH and warn once per day."""
    import shutil
    from datetime import datetime, timezone

    if shutil.which("runpod"):
        return

    flag_file = Path.home() / ".config" / "runpod-cli" / ".path-warned"
    flag_file.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")

    if flag_file.exists():
        last_warned = flag_file.read_text().strip()
        if last_warned == today:
            return

    flag_file.write_text(today)

    print("\n⚠️  Note: 'runpod' is not in your PATH.", file=sys.stderr)
    print("   You can still use: python3 -m runpod_cli", file=sys.stderr)
    print("   To add to PATH, add this to your shell config:", file=sys.stderr)
    print(f'   export PATH="{sys.prefix}/bin:$PATH"', file=sys.stderr)
    print("", file=sys.stderr)


def _get_client(ctx) -> RunPodClient:
    """Get a configured RunPod client from context."""
    if "client" not in ctx.obj:
        config = Config(ctx.obj.get("config_path"))
        api_key = config.get_api_key()
        if not api_key:
            click.echo("Error: No API key configured. Run 'runpod configure' first.", err=True)
            raise click.Abort()
        ctx.obj["client"] = RunPodClient(api_key)
        ctx.obj["config"] = config
    return ctx.obj["client"]


def _get_config(ctx) -> Config:
    """Get a Config instance from context."""
    if "config" not in ctx.obj:
        ctx.obj["config"] = Config(ctx.obj.get("config_path"))
    return ctx.obj["config"]


def handle_errors(f):
    """Decorator to catch exceptions and emit consistent error messages."""

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except click.ClickException:
            raise
        except requests.HTTPError as e:
            click.echo(f"API Error: {e}", err=True)
            if e.response is not None:
                try:
                    detail = e.response.json()
                    click.echo(json.dumps(detail, indent=2), err=True)
                except Exception:
                    click.echo(e.response.text, err=True)
            raise click.Abort()
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            raise click.Abort()

    return wrapper


@click.group()
@click.option("--config", "config_path", help="Path to config file")
@click.pass_context
def cli(ctx, config_path):
    """RunPod CLI - Generate and edit images and videos via RunPod serverless endpoints."""
    _check_path()
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config_path


@cli.command("configure")
@click.option("--api-key", help="RunPod API key")
@click.option("--config-path", help="Path to config file")
@handle_errors
def configure(api_key, config_path):
    """Configure RunPod API credentials."""
    config = Config(config_path)

    if not api_key:
        api_key = click.prompt("RunPod API key", hide_input=True)

    config.set_api_key(api_key)
    click.echo("✅ API key saved.")


@cli.group()
def image():
    """Image generation and editing commands."""
    pass


@image.command("edit")
@click.option("--prompt", "-p", required=True, help="Editing instructions")
@click.option("--image-url", "-i", multiple=True, required=True, help="Image URL(s) to edit (up to 4)")
@click.option("--safety-checker", is_flag=True, default=False, help="Enable safety checker")
@click.option(
    "--output-format",
    type=click.Choice(["png", "jpeg", "webp"]),
    help="Output image format",
)
@click.option("--aspect-ratio", help="Output aspect ratio (e.g. 16:9, 1:1, 4:3)")
@click.option("--num-images", type=int, help="Number of images to generate (batch size)")
@click.option("--seed", type=int, help="Random seed for reproducibility")
@click.option("--endpoint-id", default=DEFAULT_IMAGE_ENDPOINT, help="Override endpoint ID")
@click.option("--output", "-o", help="Save result JSON to file")
@click.option("--raw-input", help="Pass raw JSON input (overrides other options)")
@click.pass_context
@handle_errors
def image_edit(
    ctx,
    prompt,
    image_url,
    safety_checker,
    output_format,
    aspect_ratio,
    num_images,
    seed,
    endpoint_id,
    output,
    raw_input,
):
    """Edit images using the nano-banana-2-edit endpoint.

    Example:
        runpod image edit -p "make the person smile" -i https://example.com/photo.jpg
    """
    client = _get_client(ctx)

    if raw_input:
        input_data = json.loads(raw_input)
    else:
        input_data = {
            "prompt": prompt,
            "image_urls": list(image_url),
        }
        if safety_checker:
            input_data["enable_safety_checker"] = True
        if output_format:
            input_data["output_format"] = output_format
        if aspect_ratio:
            input_data["aspect_ratio"] = aspect_ratio
        if num_images is not None:
            input_data["num_images"] = num_images
        if seed is not None:
            input_data["seed"] = seed

    click.echo(f"🎨 Sending request to {endpoint_id}...")
    result = client.run_sync(endpoint_id, input_data)

    if output:
        with open(output, "w") as f:
            json.dump(result, f, indent=2)
        click.echo(f"✅ Result saved to {output}")
    else:
        click.echo(json.dumps(result, indent=2))


@cli.group()
def video():
    """Video generation commands."""
    pass


@video.command("generate")
@click.option("--prompt", "-p", required=True, help="Video generation prompt")
@click.option("--image-url", "-i", required=True, help="Source image URL")
@click.option("--num-frames", type=int, help="Number of frames to generate")
@click.option("--fps", type=int, help="Frames per second")
@click.option("--resolution", help="Video resolution (e.g. 720p, 1080p)")
@click.option("--aspect-ratio", help="Aspect ratio (e.g. 16:9, 9:16, 1:1)")
@click.option("--seed", type=int, help="Random seed for reproducibility")
@click.option("--endpoint-id", default=DEFAULT_VIDEO_ENDPOINT, help="Override endpoint ID")
@click.option("--output", "-o", help="Save result JSON to file")
@click.option("--raw-input", help="Pass raw JSON input (overrides other options)")
@click.pass_context
@handle_errors
def video_generate(
    ctx,
    prompt,
    image_url,
    num_frames,
    fps,
    resolution,
    aspect_ratio,
    seed,
    endpoint_id,
    output,
    raw_input,
):
    """Generate video from an image using the veo3-1-fast-i2v endpoint.

    Example:
        runpod video generate -p "a cat walking in a garden" -i https://example.com/cat.jpg
    """
    client = _get_client(ctx)

    if raw_input:
        input_data = json.loads(raw_input)
    else:
        input_data = {
            "prompt": prompt,
            "image_url": image_url,
        }
        if num_frames is not None:
            input_data["num_frames"] = num_frames
        if fps is not None:
            input_data["fps"] = fps
        if resolution:
            input_data["resolution"] = resolution
        if aspect_ratio:
            input_data["aspect_ratio"] = aspect_ratio
        if seed is not None:
            input_data["seed"] = seed

    click.echo(f"🎬 Sending request to {endpoint_id}...")
    result = client.run_sync(endpoint_id, input_data)

    if output:
        with open(output, "w") as f:
            json.dump(result, f, indent=2)
        click.echo(f"✅ Result saved to {output}")
    else:
        click.echo(json.dumps(result, indent=2))


@cli.group()
def job():
    """Async job management commands."""
    pass


@job.command("submit")
@click.argument("endpoint-id")
@click.argument("input-json")
@click.pass_context
@handle_errors
def job_submit(ctx, endpoint_id, input_json):
    """Submit an async job to any endpoint.

    INPUT_JSON is a JSON string or @file.json to read from file.
    """
    client = _get_client(ctx)

    if input_json.startswith("@"):
        with open(input_json[1:], "r") as f:
            input_data = json.load(f)
    else:
        input_data = json.loads(input_json)

    result = client.run_async(endpoint_id, input_data)
    click.echo(json.dumps(result, indent=2))


@job.command("status")
@click.argument("endpoint-id")
@click.argument("job-id")
@click.pass_context
@handle_errors
def job_status(ctx, endpoint_id, job_id):
    """Check status of an async job."""
    client = _get_client(ctx)
    result = client.get_status(endpoint_id, job_id)
    click.echo(json.dumps(result, indent=2))


@job.command("cancel")
@click.argument("endpoint-id")
@click.argument("job-id")
@click.pass_context
@handle_errors
def job_cancel(ctx, endpoint_id, job_id):
    """Cancel an async job."""
    client = _get_client(ctx)
    result = client.cancel_job(endpoint_id, job_id)
    click.echo(json.dumps(result, indent=2))
