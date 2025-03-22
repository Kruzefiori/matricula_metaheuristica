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
  

        # Remove columns with NotANumber, '*', or '#' in any cell
        tabela = [tab.dropna(axis=1, how='all').dropna(axis=0, how='all') for tab in tabela]
        tabela = [tab[~tab.isin(['*', '#'])] for tab in tabela]
        tabela = [tab.dropna(axis=1, how='all').dropna(axis=0, how='all') for tab in tabela]

        # Remove columns that contain: 'Ano/Período', 'Ano/Período Letivo', 'Hora Aula', 'CH', 'Turma', 'Freq %', 'NotaMín'
        tabela = [tab[~tab.astype(str).apply(lambda x: x.str.contains('Ano/Período|Ano/Período Letivo|Hora Aula|CH|Turma|Freq %|NotaMín').any(), axis=1)] for tab in tabela]

        # print first table
        print(tabela[0])


        # Salvar o resultado em JSON
        with open("sample2.txt", "w") as outfile:
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
