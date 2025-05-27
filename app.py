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
        # Get URL or custom text from the frontend
        url = request.json.get('url')
        custom_text = request.json.get('custom_text')
        voice = request.json.get('voice')
        speed = float(request.json.get('speed'))

        # Generate a unique audio filename using uuid
        audio_filename = f"static/{uuid.uuid4()}.mp3"

        # Determine the content (custom text or article from the URL)
        if custom_text:
            mytext = custom_text
        elif url:
            # Download and parse the article if a URL is provided
            article = Article(url)
            article.download()
            article.parse()
            mytext = article.text
        else:
            return jsonify({'error': 'No URL or custom text provided'}), 400

        # Validate that we have extracted some text
        if not mytext:
            return jsonify({'error': 'Failed to extract content'}), 400

        # Add a small delay to avoid hitting rate limits (if any)
        time.sleep(2)

        # Attempt using gTTS (Google Text-to-Speech) to convert text to speech
        try:
            language = 'en'
            myobj = gTTS(text=mytext, lang=language, slow=False)
            myobj.save(audio_filename)
        except Exception as e:
            # If gTTS fails, fallback to pyttsx3 (offline TTS engine)
            print(f"Error with gTTS: {e}. Falling back to offline TTS.")
            engine = pyttsx3.init()
            engine.setProperty('rate', int(speed * 150))  # Set speed dynamically
            engine.save_to_file(mytext, audio_filename)
            engine.runAndWait()

        # Return the URL of the saved audio file
        return jsonify({'audio_url': f"/{audio_filename}"})

    except Exception as e:
        # Log the error and return a JSON response with the error message
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/text_to_audio', methods=['POST'])
def text_to_audio():
    try:
        # Get the custom text from the frontend
        custom_text = request.json.get('custom_text')
        voice = request.json.get('voice')
        speed = float(request.json.get('speed'))

        # Generate a unique audio filename using uuid
        audio_filename = f"static/{uuid.uuid4()}.mp3"

        # If no custom text is provided, return an error
        if not custom_text:
            return jsonify({'error': 'No custom text provided'}), 400

        # Add a small delay to avoid rate-limiting
        time.sleep(2)

        # Attempt using gTTS to convert text to speech
        try:
            language = 'en'
            myobj = gTTS(text=custom_text, lang=language, slow=False)
            myobj.save(audio_filename)
        except Exception as e:
            # If gTTS fails, fallback to pyttsx3
            print(f"Error with gTTS: {e}. Falling back to offline TTS.")
            engine = pyttsx3.init()
            engine.save_to_file(custom_text, audio_filename)
            engine.runAndWait()

        # Return the URL to the generated audio file
        return jsonify({'audio_url': f"/{audio_filename}"})

    except Exception as e:
        # Log the error and return a JSON response with the error message
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
