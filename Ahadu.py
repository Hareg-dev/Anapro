import os
import json
import requests
import kivy
import pyaudio
import speech_recognition as sr
import pyttsx3
import vosk
import pytesseract
from gtts import gTTS
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.spinner import Spinner

class SpeechApp(App):
    def build(self):
        self.recognizer = sr.Recognizer()
        self.online_mode = self.check_internet()
        self.language = "am-ET"  # Default to Amharic

        self.layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Language Selection Dropdown
        self.language_spinner = Spinner(
            text="Amharic ",
            values=("Amharic ", "English"),
            size_hint=(1, 0.2),
        )
        self.language_spinner.bind(text=self.set_language)

        # Label for results
        self.result_label = TextInput(size_hint=(1, 0.3), readonly=True, font_size=18)

        # Buttons
        self.speech_btn = Button(text="🎤 Speak :", on_press=self.speech_to_text, size_hint=(1, 0.2))
        self.tts_btn = Button(text="🔊 Convert Text to Speech", on_press=self.text_to_speech, size_hint=(1, 0.2))
        self.ocr_btn = Button(text="📷 Extract Text from Image", on_press=self.image_extractor, size_hint=(1, 0.2))
        self.exit_btn = Button(text="❌ Exit", on_press=self.stop_app, size_hint=(1, 0.2))

        # File chooser for image upload
        self.file_chooser = FileChooserIconView(size_hint=(1, 0.3))
        
        # Input box for text-to-speech
        self.text_input = TextInput(hint_text="Enter text here ...", size_hint=(1, 0.2), font_size=18)

        # Adding widgets to layout
        self.layout.add_widget(self.language_spinner)
        self.layout.add_widget(self.speech_btn)
        self.layout.add_widget(self.tts_btn)
        self.layout.add_widget(self.text_input)
        self.layout.add_widget(self.ocr_btn)
        self.layout.add_widget(self.file_chooser)
        self.layout.add_widget(self.result_label)
        self.layout.add_widget(self.exit_btn)

        return self.layout

    def set_language(self, spinner, text):
        """Change language based on user selection."""
        if text == "Amharic":
            self.language = "am-ET"
        else:
            self.language = "en-US"

    def check_internet(self):
        """Check if internet connection exists."""
        try:
            requests.get("https://www.google.com", timeout=3)
            return True
        except requests.ConnectionError:
            return False

    def speech_to_text(self, instance):
        """Convert speech to text dynamically based on language and internet connection."""
        mic = sr.Microphone()
        with mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
            self.result_label.text = "Listening..."
            audio = self.recognizer.listen(source)

        if self.online_mode:
            text = self.online_speech_to_text(audio)
        else:
            text = self.offline_speech_to_text(audio)

        self.result_label.text = text if text else "Could not recognize speech ."

    def online_speech_to_text(self, audio):
        """Convert speech to text using Google Cloud Speech API (Online Mode)."""
        try:
            text = self.recognizer.recognize_google(audio, language=self.language)
            return f"Recognized (Online): {text}"
        except sr.UnknownValueError:
            return "Could not understand"
        except sr.RequestError as e:
            return f"Google API Error: {e}"

    def offline_speech_to_text(self, audio):
        """Convert speech to text using Vosk (Offline Mode)."""
        if self.language == "am-ET":
            model_path = "vosk-model-amharic" 
        else:
            "vosk-model-en"
            if not os.path.exists(model_path):
                return "[Error] Model not found! Download and extract it."

        model = vosk.Model(model_path)
        recognizer = vosk.KaldiRecognizer(model, 16000)

        with sr.AudioFile(audio) as source:
            audio_data = source.record()
            if recognizer.AcceptWaveform(audio_data.frame_data):
                result = json.loads(recognizer.Result())
                return f"Recognized (Offline): {result['text']}"
            else:
                return "Vosk could not process audio."

    def text_to_speech(self, instance):
        """Convert text to speech dynamically based on the selected language."""
        text = self.text_input.text
        if text:
            tts = gTTS(text=text, lang="am" if self.language == "am-ET" else "en")
            tts.save("output.mp3")
            os.system("start output.mp3")  # Play the audio
            self.result_label.text = "Converted to speech!"
        else:
            self.result_label.text = "Please enter text......"

    def image_extractor(self, instance):
        """Extract text from an image dynamically based on language."""
        file_path = self.file_chooser.selection
        if file_path:
            lang_code = "amh" if self.language == "am-ET" else "eng"
            text = pytesseract.image_to_string(file_path[0], lang=lang_code)
            self.result_label.text = f"Extracted Text: {text}"
        else:
            self.result_label.text = "[Error] No image selected!"

    def stop_app(self, instance):
        """Exit the application."""
        App.get_running_app().stop()

if __name__ == "main":
    SpeechApp().run()

