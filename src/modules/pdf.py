import pdfplumber
import argparse
import json
import tabula

#abrir o arquivo com o nome dentro da pasta datasets
def readPDF(args):
    with pdfplumber.open("./datasets/" + str(args.dataset_name)) as pdf:
        first_page = pdf.pages[0]
        print(first_page.extract_text())

#extrair cada página e montar um JSON com o conteúdo
def readPDFJSON(args):
    with pdfplumber.open("./datasets/" + str(args.dataset_name)) as pdf:
        data = []
        for page in pdf.pages:
            data.append("".join(page.extract_text()))
        
        # Ler a tabela da primeira página
        tabela = tabula.read_pdf("./datasets/" + str(args.dataset_name), pages='1', pandas_options={'header': None})
        
#TODO  - Processar a tabela em grupos de 3, cada linha do pdf do histórico gera 3 linhas na tabela de forma errada
#tem que melhorar a leitura do PDF OU agrupar essas linhas corretamente

#TODO - Salvar o resultado em JSON e limpar os dados NULL ou NAN que tem muitos

#TODO - Outra alternativa pode ser usar outra biblioteca para leitura de PDF, como o PyMuPDF (copilot quem indicou) e extrair a tabela de forma correta
#https://pymupdf.readthedocs.io/en/latest/tutorial/#extracting-text
#https://pymupdf.readthedocs.io/en/latest/tutorial/#extracting-text-into-a-json-object

        # Processar a tabela em grupos de 3
        processed_data = []
        for tab in tabela:
            rows = tab.values.tolist()  # Converter para lista de listas
            grouped_rows = [rows[i:i+3] for i in range(0, len(rows), 3)]  # Agrupar de 3 em 3
            
            # Mixar os valores dentro de cada grupo
            mixed_rows = []
            for group in grouped_rows:
                mixed_row = [item for sublist in group for item in sublist]  # Achatar o grupo
                mixed_rows.append(mixed_row)
            
            processed_data.extend(mixed_rows)
        print(processed_data)
        # Salvar o resultado em JSON
        with open("sample.txt", "w") as outfile:
            outfile.write(str(processed_data))
        
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