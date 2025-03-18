import pdfplumber
import argparse
#abrir o arquivo com o nome dentro da pasta datasets
def readPDF(args):
    with pdfplumber.open("../datasets/" + str(args.dataset_name)) as pdf:
        first_page = pdf.pages[0]
        print(first_page.extract_text())

#extrair cada página e montar um JSON com o conteúdo
def readPDFJSON(args):
    with pdfplumber.open("../datasets/" + str(args.dataset_name)) as pdf:
        data = []
        for page in pdf.pages:
            data.append(page.extract_text())
        return data