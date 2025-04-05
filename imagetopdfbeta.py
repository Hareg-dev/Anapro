import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os
from fpdf import FPDF
import pytesseract

# Make sure tesseract is installed and accessible
# If it's not installed, download and install from https://github.com/tesseract-ocr/tesseract

class ImageToPdfConverter:
    def __init__(self, root, image_dir=None):
        self.root = root
        self.image_paths = []
        self.selected_images = tk.Listbox(root)
        self.image_dir = image_dir

        self.initialise_ui()
        if image_dir:
            self.auto_select_images(image_dir)

    def initialise_ui(self):
        title_label = tk.Label(self.root, text="Image to PDF Converter", font=("Helvetica", 16, "bold"))
        title_label.pack(padx=10, pady=10)

        select_images_btn = tk.Button(self.root, text="Select Images", command=self.select_images)
        select_images_btn.pack(pady=10)

        convert_btn = tk.Button(self.root, text="Convert Images to PDF", command=self.convert_to_pdf)
        convert_btn.pack(pady=10)

        self.selected_images.pack(pady=20)

    def select_images(self):
        filepaths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        for filepath in filepaths:
            self.image_paths.append(filepath)
            self.selected_images.insert(tk.END, filepath)

    def auto_select_images(self, image_dir):
        if os.path.exists(image_dir):
            for filename in os.listdir(image_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    self.image_paths.append(os.path.join(image_dir, filename))
                    self.selected_images.insert(tk.END, os.path.join(image_dir, filename))

    def extract_text_from_images(self):
        text = ""
        for image_path in self.image_paths:
            img = Image.open(image_path)
            extracted_text = pytesseract.image_to_string(img)
            text += extracted_text + "\n"  # Append text with new lines between images
        return text

    def convert_to_pdf(self):
        if len(self.image_paths) > 0:
            # Extract text from the images
            extracted_text = self.extract_text_from_images()

            if extracted_text:
                pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
                if pdf_path:
                    pdf = FPDF()
                    pdf.set_auto_page_break(auto=True)
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)

                    # Add the extracted text to the PDF
                    pdf.multi_cell(0, 10, extracted_text)

                    # Save the PDF
                    pdf.output(pdf_path)
                    messagebox.showinfo("Success", "PDF successfully created!")
            else:
                messagebox.showerror("Error", "No text extracted from images!")
        else:
            messagebox.showerror("Error", "No images selected!")

def main():
    root = tk.Tk()
    root.title("Image to PDF Converter")

    # Automatically select images from a predefined directory (optional)
    image_dir = "path_to_your_image_folder"  # Replace with your directory path
    converter = ImageToPdfConverter(root, image_dir=image_dir)

    root.geometry("600x800")
    root.mainloop()

if __name__ == "__main__":
    main()
