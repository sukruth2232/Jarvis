import asyncio
from random import randint
from PIL import Image
import requests
import os
from dotenv import dotenv_values
from time import sleep
from pathlib import Path
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

# Set DEBUG to True to see errors in console for troubleshooting
DEBUG = False

# Configure logging
handlers = [logging.FileHandler("image_generation.log")]
if DEBUG:
    handlers.append(logging.StreamHandler())
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=handlers
)
logger = logging.getLogger(__name__)

def get_key(env_path, key_name):
    config = dotenv_values(env_path)
    return config.get(key_name, "")

def open_images(prompt):
    folder_path = Path("Data")
    folder_path.mkdir(parents=True, exist_ok=True)  # Ensure Data exists
    prompt = prompt.replace(" ", "_")
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            if not os.path.exists(image_path):
                # Create fallback red image if file is missing
                img = Image.new("RGB", (512, 512), color="red")
                img.save(image_path, "JPEG", quality=95)
                logger.info(f"Created fallback image: {image_path}")
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError as e:
            logger.error(f"Error opening image {image_path}: {e}")
            print(f"Error opening image: {image_path}")

# Use a more accessible model
API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
headers = {
    "Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"
}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def query(payload):
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
        if response.status_code == 200 and response.headers.get("content-type") == "image/jpeg":
            return response.content
        logger.error(f"Invalid API response: status={response.status_code}, content-type={response.headers.get('content-type')}, body={response.text}")
        return None
    except Exception as e:
        logger.error(f"API request failed: {e}")
        return None

async def generate_images(prompt: str):
    tasks = []

    for _ in range(4):
        seed = randint(0, 1000000)
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High details, high resolution, seed={seed}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)
    
    image_bytes_list = await asyncio.gather(*tasks)

    folder_path = Path("Data")
    folder_path.mkdir(parents=True, exist_ok=True)  # Ensure Data exists
    prompt_clean = prompt.replace(" ", "_")
    for i, image_bytes in enumerate(image_bytes_list):
        image_path = os.path.join(folder_path, f"{prompt_clean}{i+1}.jpg")
        if image_bytes is None:
            # Create fallback red image if API fails
            img = Image.new("RGB", (512, 512), color="red")
            img.save(image_path, "JPEG", quality=95)
            logger.info(f"Created fallback image: {image_path}")
        else:
            try:
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
            except Exception as e:
                logger.error(f"Error saving image {image_path}: {e}")
                img = Image.new("RGB", (512, 512), color="red")
                img.save(image_path, "JPEG", quality=95)
                logger.info(f"Created fallback image: {image_path}")

def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))    
    open_images(prompt)

while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            Data: str = f.read()
        prompt, Status = Data.strip().split(",")

        if Status == "True":
            print("Generating Images...")
            GenerateImages(prompt=prompt)

            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False,False")
            break
        else:
            sleep(1)
    except:
        pass