import pdfplumber
import re
import json
from modules import helper
from modules import statistics

# Função para extrair dados de um PDF e criar um JSON
# Recebe o nome do arquivo PDF e um parâmetro para atualizar o JSON
# Se o JSON já existir, não cria novamente
# Se o parâmetro update_json for 'y', cria um novo JSON
# Se o parâmetro update_json for 'n', não cria um novo JSON
# Se o JSON já existir, carrega os dados do JSON existente
# Se o JSON não existir, cria um novo JSON com os dados extraídos do PDF
# Se o PDF não existir, lança uma exceção
# Se o PDF não for passado, lança uma exceção
# Exemplo da estrutura montada ao final:
# {
#     "aprBySemester": {
#         "2023.1": [
#             {"disc": "Cálculo I", "nota": 7.5},
#             {"disc": "Física I", "nota": 6.0}
#         ],
#         "2023.2": [
#             {"disc": "Cálculo II", "nota": 8.0},
#             {"disc": "Física II", "nota": 5.0}
#         ]
#     },
#     "rpvBySemester": {
#         "2023.1": [
#             {"disc": "Cálculo I", "nota": 4.5},
#             {"disc": "Física I", "nota": 3.0}
#         ],
#         "2023.2": [
#             {"disc": "Cálculo II", "nota": 2.0},
#             {"disc": "Física II", "nota": 1.0}
#         ]
#     },
#     "statisticsBySemester": {
#         "2023.1": {"pctApr": 0.75, "totalMat": 4},
#         "2023.2": {"pctApr": 0.25, "totalMat": 4}
#     },
#     "missingDisciplines": [
#         "Cálculo III",
#         "Física III"
#     ],
#     "generalStatistics": {
#         "bestSemester": {"period": "2023.1", "score": 0.75},
#         "worstSemester": {"period": "2023.2", "score": 0.25},
#         "scoreAvg": 0.5
#     }
# }
def parserPdf(pdf_name, update_json):
    if not pdf_name:
        raise Exception("Para extrair o histórico, é necessário passar o nome do arquivo PDF com o parametro --dataset_name")
    # Listas para armazenar os dados
    
    #todo: verificar se o JSON já existe, se sim, não precisa criar novamente, só passar ele para o próximo passo que é o de recomendação
    json_name = re.sub(r"^historico_", "", pdf_name.split("/")[-1])
    if not helper.checkJsonExists(json_name) or update_json == 'y':
        path = "./datasets/" + pdf_name + ".pdf"
        json_path = "./__dataset_output__/" + json_name + ".json"
        
        dados = []
        disciplinas_pendentes = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                #extrai o texto da página
                text = page.extract_text()
                
                # Expressão regular para capturar Código, Média e Situação
                #padrao = re.compile(r"(\b[A-Z]{3,4}[A-Z0-9]{3,6}\b).*?(\d{1,2}\.\d|\-\-|\*)\s+(\b[A-Z]+\b)")
                #Expressão regular para capturar Código, Média e Situação e Período
                padrao = re.compile(r"(\d{4}\.\d).*?(\b[A-Z]{3,4}[A-Z0-9]{3,6}\b).*?(\d{1,2}\.\d|\-\-|\*)\s+(\b[A-Z]+\b)")

                for match in padrao.finditer(text):
                    periodo = match.group(1) # Período
                    disciplina = match.group(2)  # Código da matéria
                    nota = match.group(3)  # Nota/Média
                    situacao = match.group(4)  # Situação
                    dados.append({
                        "periodo": periodo,
                        "Disciplina": disciplina,
                        "Nota": float(nota) if nota.replace('.', '', 1).isdigit() else nota,
                        "Situação": situacao
                    })

                #regex para pegar o código da matéria e ignora Estágio/Enade/TCC
                regex_pendentes = re.compile(r"(\b[A-Z]{3,4}\d{2,3}[A-Z]?\b).*?(\d{2,3} h)")
                
                # Identifica o início da tabela de pendentes
                if "Componentes Curriculares Obrigatórios Pendentes" in text:
                    for match in regex_pendentes.finditer(text):
                        # Adiciona as disciplinas pendentes à lista
                        disciplina = match.group(1)
                        disciplinas_pendentes.append(disciplina)
                
        # Cria o JSON com os dados extraídos
        json_data = {
            "historico": dados, #para calcular médias, melhorar as possíveis recomendações
            "pendentes": disciplinas_pendentes, #analisar as pendentes
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
    else:
        with open("./__dataset_output__/" + json_name + ".json", "r", encoding="utf-8") as f:
            json_data = json.load(f)

    
    structured_data = {
        "aprBySemester" : statistics.aprBySemester(json_data),
        "rpvBySemester" : statistics.rpvBySemester(json_data),
        "statisticsBySemester" : statistics.aprRateBySemester(json_data),
        "missingDisciplines" : json_data["pendentes"]
    }
    # save structured data to a txt file
    #helper.saveIntoTxt(json_name , structured_data)
    statistics.bestAndWorsePeriod(structured_data)
    return structured_data