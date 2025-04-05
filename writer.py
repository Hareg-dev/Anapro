import os
import pytesseract
from fpdf import FPDF
from tkinter import filedialog,messagebox
import tkinter as tk
from PIL import image


def select_image():
    file_paths=filedialog.askopenfilenames(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    if file_paths:
        process_images(file_paths)

def process_images(file_paths):
    extracted_text=""
    for file in file_paths:
        text=pytesseract.image_to_string(image)

    save_to_pdf(text)

def save_to_pdf(text):
    pdf_file=filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if not pdf_file:
        return
    
    if os.path.exists(pdf_file):
        pdf=FPDF()
        pdf.set_auto_page_break(auto=True)
        pdf.set_font("Arial",size=12)
        pdf.multi_cell(0,10,text)
        pdf.output(pdf_file)
        messagebox.showinfo("succes, you make new pdf file!!!!")
    else:
        pdf=FPDF()
        pdf.set_auto_page_break(auto=True)
        pdf.set_font("Arial",size=12)
        pdf.multi_cell(0,10,text)
        pdf.output(pdf_file)
        messagebox.showinfo("you modifies the existing pdf!!!")

def main():
    root=tk.Tk()
    root.title("PDF maker")
    root.geometry("300x400")
    btn=tk.Button(root,text="select image",command=select_image)
    btn.pack()

    root.mainloop()

if __name__=="__main__":
    main

    

