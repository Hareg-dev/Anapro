import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os
from fpdf import FPDF
import pytesseract
import speech_recognition as sr
import requests
from time import sleep
import traceback

# Check internet connection
def is_connected():
    try:
        requests.get("http://www.google.com", timeout=3)
        return True
    except requests.ConnectionError:
        return False

class ImageToPdfConverter:
    def __init__(self, root, image_dir=None):
        self.root = root
        self.image_paths = []
        self.selected_images = tk.Listbox(root)
        self.image_dir = image_dir
        self.audio_file = None

        # Check if Tesseract is installed
        if not self.check_tesseract():
            messagebox.showerror("Error", "Tesseract-OCR is not installed or not found in PATH!")
            return

        self.initialise_ui()
        if image_dir and os.path.isdir(image_dir):
            self.auto_select_images(image_dir)

    def check_tesseract(self):
        try:
            pytesseract.get_tesseract_version()
            return True
        except:
            return False

    def initialise_ui(self):
        title_label = tk.Label(self.root, text="Image to PDF Converter", font=("Helvetica", 16, "bold"))
        title_label.pack(padx=10, pady=10)

        select_images_btn = tk.Button(self.root, text="Select Images", command=self.select_images)
        select_images_btn.pack(pady=10)

        convert_btn = tk.Button(self.root, text="Convert Images to PDF", command=self.convert_to_pdf)
        convert_btn.pack(pady=10)

        select_audio_btn = tk.Button(self.root, text="Select Audio for Speech-to-Text", command=self.select_audio)
        select_audio_btn.pack(pady=10)

        convert_audio_btn = tk.Button(self.root, text="Convert Audio to PDF", command=self.convert_audio_to_pdf)
        convert_audio_btn.pack(pady=10)

        self.selected_images.pack(pady=20)

    def select_images(self):
        filepaths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        for filepath in filepaths:
            self.image_paths.append(filepath)
            self.selected_images.insert(tk.END, filepath)

    def auto_select_images(self, image_dir):
        for filename in os.listdir(image_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                full_path = os.path.join(image_dir, filename)
                self.image_paths.append(full_path)
                self.selected_images.insert(tk.END, full_path)

    def extract_text_from_images(self):
        text = ""
        self.root.config(cursor="wait")  # Show loading cursor
        for image_path in self.image_paths:
            try:
                img = Image.open(image_path)
                extracted_text = pytesseract.image_to_string(img)
                text += f"Text from {os.path.basename(image_path)}:\n{extracted_text}\n\n"
            except Exception as e:
                messagebox.showwarning("Warning", f"Failed to process {image_path}: {str(e)}")
        self.root.config(cursor="")  # Reset cursor
        return text

    def convert_to_pdf(self):
        if not self.image_paths:
            messagebox.showerror("Error", "No images selected!")
            return

        extracted_text = self.extract_text_from_images()
        if not extracted_text.strip():
            messagebox.showerror("Error", "No text extracted from images!")
            return

        pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if pdf_path:
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Helvetica", size=12)  # Use Helvetica as a safer default
                pdf.multi_cell(0, 10, extracted_text.encode('latin-1', 'replace').decode('latin-1'))  # Handle encoding
                pdf.output(pdf_path)
                messagebox.showinfo("Success", "PDF successfully created!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create PDF: {str(e)}")

    def select_audio(self):
        self.audio_file = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav;*.mp3;*.ogg")])

    def convert_audio_to_pdf(self):
        if not self.audio_file:
            messagebox.showerror("Error", "No audio file selected!")
            return

        self.root.config(cursor="wait")
        if is_connected():
            self.extract_text_from_audio_online()
        else:
            self.extract_text_from_audio_offline()
        self.root.config(cursor="")

    def extract_text_from_audio_online(self):
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(self.audio_file) as source:
                audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            self.create_pdf_from_text(text)
        except sr.UnknownValueError:
            messagebox.showerror("Error", "Google Speech Recognition could not understand the audio.")
        except Exception as e:
            messagebox.showerror("Error", f"Audio processing failed: {str(e)}")

    def extract_text_from_audio_offline(self):
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(self.audio_file) as source:
                audio = recognizer.record(source)
            text = recognizer.recognize_sphinx(audio)
            self.create_pdf_from_text(text)
        except sr.UnknownValueError:
            messagebox.showerror("Error", "Offline Speech Recognition could not understand the audio.")
        except Exception as e:
            messagebox.showerror("Error", f"Offline audio processing failed: {str(e)}")

    def create_pdf_from_text(self, text):
        pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if pdf_path:
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Helvetica", size=12)
                pdf.multi_cell(0, 10, text.encode('latin-1', 'replace').decode('latin-1'))  # Handle encoding
                pdf.output(pdf_path)
                messagebox.showinfo("Success", "PDF successfully created from audio!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create PDF from audio: {str(e)}")

def main():
    root = tk.Tk()
    root.title("Image and Audio to PDF Converter")

    # Replace with actual directory or leave as None to disable auto-loading
    image_dir = None  # "path_to_your_image_folder"
    converter = ImageToPdfConverter(root, image_dir=image_dir)

    root.geometry("600x800")
    root.mainloop()

if __name__ == "__main__":
    main()