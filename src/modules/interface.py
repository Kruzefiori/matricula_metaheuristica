from modules import pdfParser
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from modules import helper



def create_UI():
    def handle_read_pdf():
        dataset_name = (combo.get()).removesuffix(".pdf") # Remove a extensão .pdf, fica mais fácil de organizar a função a seguir para criar o nome do JSON
        print(dataset_name)
        if not dataset_name:
            messagebox.showerror("Erro", "É necessário escolher um arquivo")
            return
        try:
            pdfParser.parserPdf(dataset_name , 'y')
            messagebox.showinfo("Sucesso", "Histórico importado com sucesso")
        except Exception as e:
            messagebox.showerror("Erro", f"Error: {e}")
    
    root = tk.Tk()
    root.title("Recomendação de matrícula")
    arquivos = helper.listFiles() #lista os arquivos disponíveis na pasta datasets
    btn_read_pdf = tk.Button(root, text="Read PDF", command=handle_read_pdf)
    btn_read_pdf.pack(pady=10)
    combo = ttk.Combobox(root, values=arquivos, state="readonly", width=40)
    combo.pack(pady=10)
    root.mainloop()