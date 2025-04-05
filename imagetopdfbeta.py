"""
This program allows users to convert images to PDF and also provides a
speech-to-text functionality that converts audio files into text and
saves the output in a PDF. The program works both online and offline, detecting
the network connection in real time and adjusting its behavior accordingly.
 
 """


import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from fpdf import FPDF
import pytesseract
import speech_recognition as sr
import requests
import fitz  # PyMuPDF for rendering PDFs


class PDFReader:
    def __init__(self, root):
        self.root = root
        self.pdf_document = None
        self.pdf_page = 0
        self.pdf_label = None

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not file_path:
            return
        self.pdf_document = fitz.open(file_path)
        self.pdf_page = 0
        self.display_pdf_page()

    def display_pdf_page(self):
        if self.pdf_document:
            page = self.pdf_document.load_page(self.pdf_page)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img_tk = ImageTk.PhotoImage(img)

            if self.pdf_label:
                self.pdf_label.configure(image=img_tk)
                self.pdf_label.image = img_tk
            else:
                self.pdf_label = tk.Label(self.root, image=img_tk)
                self.pdf_label.image = img_tk
                self.pdf_label.pack()

    def next_page(self):
        if self.pdf_document and self.pdf_page < len(self.pdf_document) - 1:
            self.pdf_page += 1
            self.display_pdf_page()

    def previous_page(self):
        if self.pdf_document and self.pdf_page > 0:
            self.pdf_page -= 1
            self.display_pdf_page()


class ImageToPdfConverter:
    def __init__(self):
        self.image_paths = []

    def select_images(self, filechooser, popup):
        filepaths = filechooser.selection
        for filepath in filepaths:
            self.image_paths.append(filepath)
        popup.dismiss()

    def extract_text_from_images(self):
        text = ""
        for image_path in self.image_paths:
            try:
                img = Image.open(image_path)
                text += f"Text from {os.path.basename(image_path)}:\n{pytesseract.image_to_string(img)}\n\n"
            except Exception as e:
                messagebox.showwarning("Warning", f"Failed to process {image_path}: {str(e)}")
        return text

    def save_pdf(self, text):
        pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if pdf_path:
            try:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, text.encode('latin-1', 'replace').decode('latin-1'))
                pdf.output(pdf_path)
                messagebox.showinfo("Success", "PDF successfully created!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create PDF: {str(e)}")


class AudioToPdfConverter:
    def __init__(self):
        self.audio_file = None

    def select_audio(self):
        filepaths = filedialog.askopenfilenames(filetypes=[("Audio Files", "*.wav;*.mp3;*.ogg")])
        if filepaths:
            self.audio_file = filepaths[0]

    def process_audio_to_pdf(self):
        if not self.audio_file:
            messagebox.showerror("Error", "No audio file selected!")
            return
        text = self.extract_text_from_audio()
        if text:
            ImageToPdfConverter().save_pdf(text)

    def extract_text_from_audio(self):
        recognizer = sr.Recognizer()
        try:
            with sr.AudioFile(self.audio_file) as source:
                audio = recognizer.record(source)
                if self.is_connected():
                    try:
                        return recognizer.recognize_google(audio)
                    except sr.RequestError:
                        messagebox.showwarning("Warning", "Google Speech Recognition service is unavailable.")
                return recognizer.recognize_sphinx(audio)
        except sr.UnknownValueError:
            messagebox.showerror("Error", "Speech Recognition could not understand the audio.")
        except Exception as e:
            messagebox.showerror("Error", f"Audio processing failed: {str(e)}")
        return None

    @staticmethod
    def is_connected():
        try:
            requests.get("http://www.google.com", timeout=3)
            return True
        except requests.ConnectionError:
            return False


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.image_converter = ImageToPdfConverter()
        self.audio_converter = AudioToPdfConverter()
        self.pdf_reader = PDFReader(self.master)
        self.create_widgets()

    def create_widgets(self):
        self.title_label = tk.Label(self.master, text="Image to PDF Converter", font=("Helvetica", 16, "bold"))
        self.title_label.pack(padx=10, pady=10)

        # Image conversion
        self.select_images_btn = tk.Button(self.master, text="Select Images", command=self.select_images)
        self.select_images_btn.pack(pady=10)

        self.convert_btn = tk.Button(self.master, text="Convert Images to PDF", command=self.convert_to_pdf)
        self.convert_btn.pack(pady=10)

        # Audio conversion
        self.select_audio_btn = tk.Button(self.master, text="Select Audio for Speech-to-Text", command=self.select_audio)
        self.select_audio_btn.pack(pady=10)

        self.convert_audio_btn = tk.Button(self.master, text="Convert Audio to PDF", command=self.convert_audio_to_pdf)
        self.convert_audio_btn.pack(pady=10)

        # PDF Reader
        self.open_pdf_btn = tk.Button(self.master, text="Open PDF", command=self.pdf_reader.open_pdf)
        self.open_pdf_btn.pack(pady=10)

        self.next_page_btn = tk.Button(self.master, text="Next Page", command=self.pdf_reader.next_page)
        self.next_page_btn.pack(pady=5)

        self.prev_page_btn = tk.Button(self.master, text="Previous Page", command=self.pdf_reader.previous_page)
        self.prev_page_btn.pack(pady=5)

    def select_images(self):
        filechooser = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        self.image_converter.select_images(filechooser, self)

    def convert_to_pdf(self):
        text = self.image_converter.extract_text_from_images()
        if not text.strip():
            messagebox.showerror("Error", "No text extracted from images!")
            return
        self.image_converter.save_pdf(text)

    def select_audio(self):
        self.audio_converter.select_audio()

    def convert_audio_to_pdf(self):
        self.audio_converter.process_audio_to_pdf()


def main():
    root = tk.Tk()
    root.title("Image to PDF Converter with PDF Reader")

    # Set window size
    root.geometry("600x800")

    # Initialize and start the application
    app = Application(master=root)
    app.mainloop()


if __name__ == "__main__":
    main()
