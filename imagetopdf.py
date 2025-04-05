import tkinter as tk
from tkinter import filedialog
#from PILLOW import Image
import os


class Image_to_pdf_Converter:
    def __init(self,root):
        self.root=root
        self.image_paths=[]
        self.outpdfname=tk.StringVar()
        self.selected_images=tk.Listbox(root)

        self.initialise_ui()

    def intialise_ui(self):
        title_label=tk.Label(tk.root,text="image to pdf convertor",font=("Helvetica",16,"bold"))
        title_label.pack(padx=10,pady=10)

        select_images_btn=tk.Button(tk.root,text="select",command=select_images)
        select_images_btn.pack()



def main():
    root=tk.Tk()
    root.title("Image to Pdf Convertor")
    convertor=Image_to_pdf_Converter(root)
    root.geometry("400x600")
    root.mainloop()


if __name__ == "__main__":
    main()


    