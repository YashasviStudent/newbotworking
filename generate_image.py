import base64
import mimetypes
import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables from .env file
load_dotenv()

def save_binary_file(file_name, data):
    with open(file_name, "wb") as f:
        f.write(data)
    return file_name

def generate_image(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in environment.", file=sys.stderr)
        sys.exit(1)
    client = genai.Client(api_key=api_key)

    model = "gemini-2.0-flash-preview-image-generation"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_modalities=["IMAGE", "TEXT"]
        # Do NOT specify response_mime_type here!
    )

    file_index = 0
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
        part = chunk.candidates[0].content.parts[0]
        if hasattr(part, "inline_data") and part.inline_data and part.inline_data.data:
            inline_data = part.inline_data
            data_buffer = inline_data.data
            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            if not file_extension:
                file_extension = ".jpeg"
            file_name = f"generated_image_{file_index}{file_extension}"
            file_index += 1
            saved_path = save_binary_file(file_name, data_buffer)
            print(saved_path)
            return  # Only handle one image per call
        else:
            pass

    print("Error: No image data received from Gemini.", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_image.py <prompt>")
        sys.exit(1)
    prompt_from_node = sys.argv[1]
    generate_image(prompt_from_node)