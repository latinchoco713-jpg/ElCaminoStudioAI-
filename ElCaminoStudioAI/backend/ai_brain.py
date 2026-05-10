import random
import os

def generate_music(prompt):
    # Simulate AI music generation
    # In a real implementation, use libraries like Magenta or OpenAI API
    notes = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4']
    melody = [random.choice(notes) for _ in range(16)]

    # For now, just return a path to a placeholder
    output_path = os.path.join('output', f'music_{random.randint(1000,9999)}.wav')
    # In real implementation, generate and save the audio file
    return output_path

def generate_lyrics(prompt):
    # Try OpenAI GPT first, fallback to simple generation
    try:
        import openai
        import os

        # Check if API key is available
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un compositor de letras de canciones. Crea letras emotivas y poéticas en español."},
                    {"role": "user", "content": f"Crea una letra de canción basada en: {prompt}"}
                ],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
    except ImportError:
        pass
    except Exception as e:
        print(f"OpenAI API error: {e}")

    # Fallback to simple generation
    words = ['amor', 'vida', 'música', 'camino', 'emoción', 'sueño', 'esperanza', 'corazón', 'alma', 'recuerdos']
    lyrics = ' '.join(random.sample(words, 8))
    return f"Letra generada: {lyrics}"

def generate_image(prompt, output_dir='assets/clips'):
    """
    Generate an image using OpenAI DALL-E first, then Stable Diffusion, then placeholder
    """
    try:
        import openai
        import os
        from PIL import Image
        import requests
        from io import BytesIO

        # Try OpenAI DALL-E first
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            client = openai.OpenAI(api_key=api_key)
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            # Download and save the image
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            image = Image.open(BytesIO(image_response.content))

            os.makedirs(output_dir, exist_ok=True)
            image_path = os.path.join(output_dir, f'dalle_{random.randint(1000,9999)}.png')
            image.save(image_path)
            return image_path

    except ImportError:
        pass
    except Exception as e:
        print(f"OpenAI DALL-E error: {e}")

    # Fallback to Stable Diffusion
    try:
        from diffusers import StableDiffusionPipeline
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model_id = "CompVis/stable-diffusion-v1-4"

        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        )
        pipe = pipe.to(device)

        with torch.autocast(device):
            image = pipe(prompt, num_inference_steps=20, guidance_scale=7.5).images[0]

        os.makedirs(output_dir, exist_ok=True)
        image_path = os.path.join(output_dir, f'sd_{random.randint(1000,9999)}.png')
        image.save(image_path)
        return image_path

    except ImportError:
        print("Diffusers library not available. Using placeholder image generation.")
    except Exception as e:
        print(f"Stable Diffusion error: {e}")

    # Final fallback to placeholder
    return generate_placeholder_image(prompt, output_dir)

def generate_placeholder_image(prompt, output_dir='assets/clips'):
    """
    Generate a simple placeholder image when AI generation is not available
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import textwrap

        # Create a simple colored background based on prompt keywords
        colors = {
            'oscuro': '#2C1810',
            'luz': '#F5F5DC',
            'rojo': '#8B0000',
            'azul': '#00008B',
            'verde': '#006400',
            'amarillo': '#FFD700'
        }

        bg_color = '#4A4A4A'  # Default gray
        for keyword, color in colors.items():
            if keyword in prompt.lower():
                bg_color = color
                break

        # Create image
        img = Image.new('RGB', (800, 600), color=bg_color)
        draw = ImageDraw.Draw(img)

        # Add text
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()

        # Wrap text
        wrapped_text = textwrap.wrap(prompt, width=30)
        y_position = 200

        for line in wrapped_text:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x_position = (800 - text_width) // 2
            draw.text((x_position, y_position), line, fill='white', font=font)
            y_position += 50

        # Save image
        os.makedirs(output_dir, exist_ok=True)
        image_path = os.path.join(output_dir, f'placeholder_{random.randint(1000,9999)}.png')
        img.save(image_path)

        return image_path

    except Exception as e:
        print(f"Error creating placeholder image: {e}")
        return None