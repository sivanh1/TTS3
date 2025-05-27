from flask import Flask, render_template, request, jsonify
from newspaper import Article
from gtts import gTTS
import pyttsx3
import os
import time
import uuid

app = Flask(__name__)

# Ensure the 'static' directory exists for storing audio files
if not os.path.exists('static'):
    os.makedirs('static')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    try:
        url = request.json.get('url')
        custom_text = request.json.get('custom_text')
        voice = request.json.get('voice')
        speed = float(request.json.get('speed'))

        audio_filename = f"static/{uuid.uuid4()}.mp3"

        if custom_text:
            mytext = custom_text
        elif url:
            article = Article(url)
            article.download()
            article.parse()
            mytext = article.text
        else:
            return jsonify({'error': 'No URL or custom text provided'}), 400

        if not mytext:
            return jsonify({'error': 'Failed to extract content'}), 400

        time.sleep(2)

        try:
            language = 'en'
            myobj = gTTS(text=mytext, lang=language, slow=False)
            myobj.save(audio_filename)
        except Exception as e:
            print(f"Error with gTTS: {e}. Falling back to offline TTS.")
            engine = pyttsx3.init()
            engine.setProperty('rate', int(speed * 150))
            engine.save_to_file(mytext, audio_filename)
            engine.runAndWait()

        return jsonify({'audio_url': f"/{audio_filename}"})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/text_to_audio', methods=['POST'])
def text_to_audio():
    try:
        custom_text = request.json.get('custom_text')
        voice = request.json.get('voice')
        speed = float(request.json.get('speed'))

        audio_filename = f"static/{uuid.uuid4()}.mp3"

        if not custom_text:
            return jsonify({'error': 'No custom text provided'}), 400

        time.sleep(2)

        try:
            language = 'en'
            myobj = gTTS(text=custom_text, lang=language, slow=False)
            myobj.save(audio_filename)
        except Exception as e:
            print(f"Error with gTTS: {e}. Falling back to offline TTS.")
            engine = pyttsx3.init()
            engine.setProperty('rate', int(speed * 150))
            engine.save_to_file(custom_text, audio_filename)
            engine.runAndWait()

        return jsonify({'audio_url': f"/{audio_filename}"})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

# Deployment-safe app launch
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
