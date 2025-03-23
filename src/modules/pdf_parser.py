import pdfplumber
import re
import json

def parser_pdf_to_json(pdf_path):
    # Listas para armazenar os dados
    dados = []
    json_name = re.sub(r"^historico_", "", pdf_path.split("/")[-1])
    path = "./datasets/" + pdf_path + ".pdf"
    json_path = "./__dataset_output__/" + json_name + ".json"
    print(json_path)

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            
            # Expressão regular para capturar Código, Média e Situação
            padrao = re.compile(r"(\b[A-Z]{3,4}[A-Z0-9]{3,6}\b).*?(\d{1,2}\.\d|\-\-|\*)\s+(\b[A-Z]+\b)")
            
            for match in padrao.finditer(text):
                disciplina = match.group(1)  # Código da matéria
                nota = match.group(2)  # Nota/Média
                situacao = match.group(3)  # Situação
                dados.append({
                    "Disciplina": disciplina,
                    "Nota": nota,  
                    "Situação": situacao
                })
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)