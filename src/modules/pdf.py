import pdfplumber
import argparse
import json
import tabula
import pandas as pd
from pdfquery import PDFQuery


#extrair cada página e montar um JSON com o conteúdo
def readPDFJSON(args):
    with pdfplumber.open("./datasets/" + str(args.dataset_name)) as pdf:
        # Ler a tabela da primeira página
        tabela = tabula.read_pdf("./datasets/" + str(args.dataset_name), pages='all', pandas_options={'header': None})
        
#TODO  - Processar a tabela em grupos de 3, cada linha do pdf do histórico gera 3 linhas na tabela de forma errada
#tem que melhorar a leitura do PDF OU agrupar essas linhas corretamente

#TODO - Salvar o resultado em JSON e limpar os dados NULL ou NAN que tem muitos

#TODO - Outra alternativa pode ser usar outra biblioteca para leitura de PDF, como o PyMuPDF (copilot quem indicou) e extrair a tabela de forma correta
#https://pymupdf.readthedocs.io/en/latest/tutorial/#extracting-text
#https://pymupdf.readthedocs.io/en/latest/tutorial/#extracting-text-into-a-json-object
  
        # Remover valores NaN e Null da tabela
        # Processar a tabela em grupos de 3
        #print(tabela)
        print("------------------- 0")
        #print(len(tabela))
        print(tabela)
        print("------------------- 1")
        print(tabela[1])
        print("------------------- 2")
        print(tabela[2])

        # Salvar o resultado em JSON
        with open("sample.txt", "w") as outfile:
            outfile.write(str(tabela))
        
        return ''
    

#só para não lembrar, essa está funcionando mas não está agrupando as linhas corretamente       
def readPDFJ1SON(args):

    with pdfplumber.open("./datasets/" + str(args.dataset_name)) as pdf:
        data = []
        for page in pdf.pages:
            data.append("".join(page.extract_text()))
        tabela = tabula.read_pdf("./datasets/" + str(args.dataset_name), pages='1')
        with open("sample.json", "w") as outfile:
            for tab in tabela:
                outfile.write(tab.to_json(orient="records"))
        return ''