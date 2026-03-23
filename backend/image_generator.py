import os
import io
import time
import base64
import requests
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

STYLE_PROMPTS = {
    "Modern": "modern minimalist clean lines neutral colors contemporary",
    "Classic": "classic elegant traditional symmetrical timeless",
    "Vintage": "vintage retro warm tones antique furniture nostalgic",
    "Luxury": "luxury gold accents marble velvet expensive opulent",
    "Scandinavian": "scandinavian minimalist natural wood white cozy",
    "Bohemian": "bohemian colorful eclectic artistic boho chic",
    "Industrial": "industrial exposed brick metal raw wood urban loft",
    "Japanese": "japanese zen minimal natural materials peaceful"
}


def build_prompt(user_prompt, style, room_type):
    style_keywords = STYLE_PROMPTS.get(style, "modern minimalist")
    full_prompt = (
        f"{room_type} interior design, "
        f"{user_prompt}, "
        f"{style_keywords}, "
        f"highly detailed, professional photography, "
        f"4k quality, beautiful lighting, realistic, "
        f"furnished room, decorated interior"
    )
    return full_prompt


def resize_image(image_path):
    """Resize image to 1024x1024 as required by Stability AI SDXL."""
    try:
        print(f"Resizing image: {image_path}")
        img = Image.open(image_path)

        # Convert to RGB if needed
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Resize to 1024x1024
        img = img.resize((1024, 1024), Image.LANCZOS)

        # Save to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        print("✅ Image resized to 1024x1024 successfully")
        return img_bytes.read(), "image/png"

    except Exception as e:
        print(f"❌ Resize error: {e}")
        return None, None


def generate_image(user_prompt, style="Modern", room_type="Living Room", image_path=None):
    try:
        stability_key = os.environ.get("STABILITY_API_KEY")

        if not stability_key:
            return None, "Missing STABILITY_API_KEY in .env file"

        full_prompt = build_prompt(user_prompt, style, room_type)
        print(f"Generating with prompt: {full_prompt}")

        # Use image-to-image if image is provided
        if image_path and os.path.exists(image_path):
            print(f"✅ Image found: {image_path}")
            print("Using Image-to-Image mode...")
            return generate_image_to_image(stability_key, full_prompt, image_path)
        else:
            print(f"❌ Image not found: {image_path}")
            print("Using Text-to-Image mode...")
            return generate_text_to_image(stability_key, full_prompt)

    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again"

    except requests.exceptions.ConnectionError:
        return None, "No internet connection"

    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


def generate_image_to_image(stability_key, full_prompt, image_path):
    """Generate interior design based on existing room image."""
    try:
        # Resize image to 1024x1024
        image_data, mime_type = resize_image(image_path)

        if not image_data:
            print("Resize failed, falling back to Text-to-Image...")
            return generate_text_to_image(stability_key, full_prompt)

        print("Sending Image-to-Image request to Stability AI...")

        response = requests.post(
            "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/image-to-image",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {stability_key}"
            },
            files={
                "init_image": (
                    "room.png",
                    image_data,
                    mime_type
                )
            },
            data={
                "init_image_mode": "STEP_SCHEDULE",
                "step_schedule_start": 0.65,
                "step_schedule_end": 0.0,
                "steps": 50,
                "seed": 0,
                "cfg_scale": 12,
                "samples": 1,
                "text_prompts[0][text]": full_prompt,
                "text_prompts[0][weight]": 1,
                "text_prompts[1][text]": "ugly, blurry, low quality, dark, empty room",
                "text_prompts[1][weight]": -1
            },
            timeout=120
        )

        print(f"Image-to-Image status: {response.status_code}")
        print(f"Image-to-Image response: {response.text[:200]}")

        if response.status_code == 200:
            data = response.json()
            image_data = base64.b64decode(
                data["artifacts"][0]["base64"]
            )
            print("✅ Image-to-Image success!")
            return save_image(image_data)

        else:
            print(f"Image-to-Image failed: {response.text[:200]}")
            print("Falling back to Text-to-Image...")
            return generate_text_to_image(stability_key, full_prompt)

    except Exception as e:
        print(f"Image-to-Image error: {e}")
        print("Falling back to Text-to-Image...")
        return generate_text_to_image(stability_key, full_prompt)


def generate_text_to_image(stability_key, full_prompt):
    """Generate image from text prompt only."""
    try:
        response = requests.post(
            "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {stability_key}"
            },
            json={
                "text_prompts": [
                    {
                        "text": full_prompt,
                        "weight": 1
                    },
                    {
                        "text": "ugly, blurry, low quality, empty room, dark",
                        "weight": -1
                    }
                ],
                "cfg_scale": 7,
                "height": 1024,
                "width": 1024,
                "steps": 30,
                "samples": 1
            },
            timeout=120
        )

        print(f"Text-to-Image status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            image_data = base64.b64decode(
                data["artifacts"][0]["base64"]
            )
            print("✅ Text-to-Image success!")
            return save_image(image_data)
        else:
            return None, f"Error: {response.text[:200]}"

    except Exception as e:
        return None, f"Text-to-Image error: {str(e)}"


def save_image(content):
    timestamp = int(time.time())
    output_filename = f"generated_design_{timestamp}.png"
    output_folder = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "generated_images"
    )
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, output_filename)

    with open(output_path, "wb") as f:
        f.write(content)

    print(f"✅ Image saved: {output_path}")
    return output_path, None


def test_generator():
    print("Testing image generator...")
    path, error = generate_image(
        user_prompt="cozy living room with warm lighting",
        style="Modern",
        room_type="Living Room"
    )
    if error:
        print(f"❌ Error: {error}")
    else:
        print(f"✅ Image generated at: {path}")


if __name__ == "__main__":
    test_generator()