"""
This program allows users to convert images to PDF and also provides a 
speech-to-text functionality that converts audio files into text and saves the 
output in a PDF. The program works both online and offline, detecting the 
network connection in real time and adjusting its behavior accordingly.

"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.image import Image as KivyImage
from kivy.clock import Clock
from PIL import Image
import os
from fpdf import FPDF
import pytesseract
import speech_recognition as sr
import requests
import fitz  # PyMuPDF for PDF rendering
from kivy.core.image import Image as CoreImage
from io import BytesIO

# Check internet connection
def is_connected():
    try:
        requests.get("http://www.google.com", timeout=3)
        return True
    except requests.ConnectionError:
        return False

class ImageToPdfApp(App):
    def __init__(self):
        super().__init__()
        self.image_paths = []
        self.audio_file = None
        self.status_label = None
        self.pdf_path = None
        self.pdf_document = None
        self.current_page = 0
        self.total_pages = 0

    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Title
        title = Label(text="Image & Audio to PDF", font_size=24, size_hint=(1, 0.1))
        self.layout.add_widget(title)

        # Buttons
        select_images_btn = Button(text="Select Images", size_hint=(1, 0.1))
        select_images_btn.bind(on_press=self.select_images)
        self.layout.add_widget(select_images_btn)

        convert_images_btn = Button(text="Convert Images to PDF", size_hint=(1, 0.1))
        convert_images_btn.bind(on_press=self.convert_to_pdf)
        self.layout.add_widget(convert_images_btn)

        select_audio_btn = Button(text="Select Audio", size_hint=(1, 0.1))
        select_audio_btn.bind(on_press=self.select_audio)
        self.layout.add_widget(select_audio_btn)

        convert_audio_btn = Button(text="Convert Audio to PDF", size_hint=(1, 0.1))
        convert_audio_btn.bind(on_press=self.convert_audio_to_pdf)
        self.layout.add_widget(convert_audio_btn)

        read_pdf_btn = Button(text="Read PDF", size_hint=(1, 0.1))
        read_pdf_btn.bind(on_press=self.open_pdf_reader)
        self.layout.add_widget(read_pdf_btn)

        # Status Label
        self.status_label = Label(text="Ready", size_hint=(1, 0.1))
        self.layout.add_widget(self.status_label)

        return self.layout

    def show_popup(self, title, content):
        popup = Popup(title=title, content=Label(text=content), size_hint=(0.8, 0.4))
        popup.open()

    def select_files(self, file_type, callback):
        file_chooser = FileChooserListView(filters=file_type)
        popup_layout = BoxLayout(orientation='vertical')
        popup_layout.add_widget(file_chooser)
        select_btn = Button(text="Select", size_hint=(1, 0.2))
        popup = Popup(title="Choose Files", content=popup_layout, size_hint=(0.9, 0.9))

        def on_select(instance):
            selected = file_chooser.selection
            if selected:
                callback(selected)
            popup.dismiss()

        select_btn.bind(on_press=on_select)
        popup_layout.add_widget(select_btn)
        popup.open()

    def select_images(self, instance):
        self.select_files(["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif"], self.on_images_selected)

    def on_images_selected(self, selected):
        self.image_paths = selected
        self.status_label.text = f"Selected {len(selected)} images"

    def select_audio(self, instance):
        self.select_files(["*.wav", "*.mp3", "*.ogg"], self.on_audio_selected)

    def on_audio_selected(self, selected):
        if selected:
            self.audio_file = selected[0]
            self.status_label.text = f"Selected audio: {os.path.basename(self.audio_file)}"

    def extract_text_from_images(self):
        text = ""
        for image_path in self.image_paths:
            try:
                img = Image.open(image_path)
                extracted_text = pytesseract.image_to_string(img)
                text += f"Text from {os.path.basename(image_path)}:\n{extracted_text}\n\n"
            except Exception as e:
                self.show_popup("Warning", f"Failed to process {image_path}: {str(e)}")
        return text

    def convert_to_pdf(self, instance):
        if not self.image_paths:
            self.show_popup("Error", "No images selected!")
            return

        self.status_label.text = "Processing images..."
        Clock.schedule_once(lambda dt: self._convert_to_pdf(), 0.1)

    def _convert_to_pdf(self):
        extracted_text = self.extract_text_from_images()
        if not extracted_text.strip():
            self.show_popup("Error", "No text extracted from images!")
            self.status_label.text = "Ready"
            return

        self.pdf_path = os.path.join(os.getcwd(), "output.pdf")
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=12)
            pdf.multi_cell(0, 10, extracted_text.encode('latin-1', 'replace').decode('latin-1'))
            pdf.output(self.pdf_path)
            self.show_popup("Success", f"PDF saved as {self.pdf_path}")
            self.status_label.text = "Ready"
        except Exception as e:
            self.show_popup("Error", f"Failed to create PDF: {str(e)}")
            self.status_label.text = "Ready"

    def convert_audio_to_pdf(self, instance):
        if not self.audio_file:
            self.show_popup("Error", "No audio file selected!")
            return

        self.status_label.text = "Processing audio..."
        Clock.schedule_once(lambda dt: self._convert_audio_to_pdf(), 0.1)

    def _convert_audio_to_pdf(self):
        if is_connected():
            self.extract_text_from_audio_online()
        else:
            self.extract_text_from_audio_offline()

    def extract_text_from_audio_online(self):
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(self.audio_file) as source:
                audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            self.create_pdf_from_text(text)
        except sr.UnknownValueError:
            self.show_popup("Error", "Google Speech Recognition could not understand the audio.")
            self.status_label.text = "Ready"
        except Exception as e:
            self.show_popup("Error", f"Audio processing failed: {str(e)}")
            self.status_label.text = "Ready"

    def extract_text_from_audio_offline(self):
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(self.audio_file) as source:
                audio = recognizer.record(source)
            text = recognizer.recognize_sphinx(audio)
            self.create_pdf_from_text(text)
        except sr.UnknownValueError:
            self.show_popup("Error", "Offline Speech Recognition could not understand the audio.")
            self.status_label.text = "Ready"
        except Exception as e:
            self.show_popup("Error", f"Offline audio processing failed: {str(e)}")
            self.status_label.text = "Ready"

    def create_pdf_from_text(self, text):
        self.pdf_path = os.path.join(os.getcwd(), "audio_output.pdf")
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=12)
            pdf.multi_cell(0, 10, text.encode('latin-1', 'replace').decode('latin-1'))
            pdf.output(self.pdf_path)
            self.show_popup("Success", f"PDF saved as {self.pdf_path}")
            self.status_label.text = "Ready"
        except Exception as e:
            self.show_popup("Error", f"Failed to create PDF from audio: {str(e)}")
            self.status_label.text = "Ready"

    def open_pdf_reader(self, instance):
        self.select_files(["*.pdf"], self.load_pdf)

    def load_pdf(self, selected):
        if not selected:
            return
        self.pdf_path = selected[0]
        try:
            self.pdf_document = fitz.open(self.pdf_path)
            self.total_pages = self.pdf_document.page_count
            self.current_page = 0
            self.show_pdf_reader()
        except Exception as e:
            self.show_popup("Error", f"Failed to open PDF: {str(e)}")

    def show_pdf_reader(self):
        reader_layout = BoxLayout(orientation='vertical')
        popup = Popup(title=f"PDF Reader: {os.path.basename(self.pdf_path)}", content=reader_layout, size_hint=(0.9, 0.9))

        # Render current page as an image
        page = self.pdf_document.load_page(self.current_page)
        pix = page.get_pixmap()
        img_data = BytesIO(pix.tobytes("png"))
        kivy_img = CoreImage(img_data, ext="png")
        image_widget = KivyImage(texture=kivy_img.texture)
        reader_layout.add_widget(image_widget)

        # Navigation buttons
        nav_layout = BoxLayout(size_hint=(1, 0.1))
        prev_btn = Button(text="Previous")
        prev_btn.bind(on_press=self.prev_page)
        next_btn = Button(text="Next")
        next_btn.bind(on_press=self.next_page)
        page_label = Label(text=f"Page {self.current_page + 1}/{self.total_pages}")
        nav_layout.add_widget(prev_btn)
        nav_layout.add_widget(page_label)
        nav_layout.add_widget(next_btn)
        reader_layout.add_widget nav_layout)

        popup.open()

    def prev_page(self, instance):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_pdf_reader()

    def next_page(self, instance):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.show_pdf_reader()

if __name__ == "__main__":
    ImageToPdfApp().run()