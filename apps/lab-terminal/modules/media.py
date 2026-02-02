import base64
import struct
import os
import uuid
from flask import Blueprint, request, jsonify, url_for
from google.genai import types
from .core import client
from .db import log_message

media_bp = Blueprint('media', __name__)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), '../static/assets')
os.makedirs(ASSETS_DIR, exist_ok=True)

def add_wav_header(pcm_data, sample_rate=24000, num_channels=1, sample_width=2):
    file_length = len(pcm_data) + 44 - 8
    header = b'RIFF' + struct.pack('<I', file_length) + b'WAVE' + \
             b'fmt ' + struct.pack('<I', 16) + \
             struct.pack('<H', 1) + struct.pack('<H', num_channels) + \
             struct.pack('<I', sample_rate) + \
             struct.pack('<I', sample_rate * num_channels * sample_width) + \
             struct.pack('<H', num_channels * sample_width) + \
             struct.pack('<H', sample_width * 8) + \
             b'data' + struct.pack('<I', len(pcm_data))
    return header + pcm_data

@media_bp.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.json
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    # Log the prompt
    log_message('main', 'user', 'OPERATOR', f"IMAGE REQUEST: {prompt}", 'text')

    try:
        response = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                include_rai_reason=True,
                output_mime_type='image/png'
            )
        )
        image_bytes = response.generated_images[0].image.image_bytes
        
        # Save to Vault
        image_id = str(uuid.uuid4())[:8]
        filename = f"{image_id}.png"
        filepath = os.path.join(ASSETS_DIR, filename)
        
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
            
        # Return local URL
        image_url = f"/static/assets/{filename}"
        
        # Log the result
        log_message('main', 'bot', 'IMAGEN_CORE', image_url, 'image')
        
        return jsonify({'image_url': image_url, 'id': image_id})
    except Exception as e:
        log_message('main', 'system', 'CORE', f"// IMG ERROR: {str(e)}", 'text')
        return jsonify({'error': str(e)}), 500

@media_bp.route('/vault', methods=['GET'])
def list_vault():
    try:
        files = sorted(os.listdir(ASSETS_DIR), key=lambda x: os.path.getmtime(os.path.join(ASSETS_DIR, x)), reverse=True)
        images = [f"/static/assets/{f}" for f in files if f.endswith('.png')]
        return jsonify({'images': images})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# ... (rest of file)
def list_vault():
    try:
        files = sorted(os.listdir(ASSETS_DIR), key=lambda x: os.path.getmtime(os.path.join(ASSETS_DIR, x)), reverse=True)
        images = [f"/static/assets/{f}" for f in files if f.endswith('.png')]
        return jsonify({'images': images})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@media_bp.route('/tts', methods=['POST'])
def tts():
    data = request.json
    text = data.get('text')
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash-preview-tts',
            contents=[f"Convert this text to speech: {text}"],
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name='puck'
                        )
                    )
                )
            )
        )
        audio_data = None
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                audio_data = part.inline_data.data
                break
        
        if audio_data:
            wav_data = add_wav_header(audio_data)
            encoded_audio = base64.b64encode(wav_data).decode('utf-8')
            return jsonify({'audio_url': f"data:audio/wav;base64,{encoded_audio}"})
        return jsonify({'error': 'No audio data found'}), 500
    except Exception as e:
        error_str = str(e)
        if "429" in error_str:
            return jsonify({'error': "Voice engine cooling down"}), 429
        return jsonify({'error': f"TTS Failed: {error_str}"}), 500
