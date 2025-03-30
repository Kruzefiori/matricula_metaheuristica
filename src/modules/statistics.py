import math

# aprRateBySemester: Calcula a razão de aprovados por total de disciplinas cursadas
# e retorna um dicionário com as estatísticas por semestre
#         # Extrai os dados do PDF
# Exemplo de saída:
# {
#     "2023.1": {"pctApr": 0.75, "totalMat": 4},
#     "2023.2": {"pctApr": 0.25, "totalMat": 4}
# }
#     }
# Exemplo de dados extraídos
#     dados = [
#         {"periodo": "2023.1", "Disciplina": "Cálculo I", "Nota": 7.5, "Situação": "APR"},
#         {"periodo": "2023.1", "Disciplina": "Física I", "Nota": 6.0, "Situação": "APR"},
#         {"periodo": "2023.1", "Disciplina": "Cálculo II", "Nota": 4.5, "Situação": "RPV"},
#         {"periodo": "2023.2", "Disciplina": "Cálculo II", "Nota": 8.0, "Situação": "APR"},
#         {"periodo": "2023.2", "Disciplina": "Física II", "Nota": 5.0, "Situação": "APR"},
#         {"periodo": "2023.2", "Disciplina": "Física III", "Nota": 2.0, "Situação": "RPV"},
#         {"periodo": "2023.2", "Disciplina": "Cálculo III", "Nota": 1.0, "Situação": "RPV"}
#]
def aprRateBySemester(json_data):
    historico = json_data["historico"]
    periodos = {}

    # Processa o histórico para contar aprovados e o total por período
    for item in historico:
        periodo = item["periodo"]
        situacao = item["Situação"]
        # Se a situação for "MATR", não conta como aprovado
        if situacao == "MATR":
            continue
        if periodo not in periodos:
            periodos[periodo] = {"aprovadas": 0, "total": 0}
        periodos[periodo]["total"] += 1
        if item["Situação"] == "APR":
            periodos[periodo]["aprovadas"] += 1
    # Calcula a razão de aprovados por total por período
    resultados = {periodo: {"pctApr" : round(periodos[periodo]["aprovadas"] / periodos[periodo]["total"] , 2) , "totalMat" : periodos[periodo]["total"]} for periodo in periodos}
    return resultados

# Agrupa as disciplinas por semestre, separando as aprovadas (APR) e reprovadas (RPV)
# e retorna um dicionário com as disciplinas e notas
# de cada semestre
# Exemplo de saída:
# {
#     "2023.1": [
#         {"disc": "Cálculo I", "nota": 7.5},
#         {"disc": "Física I", "nota": 6.0}
#     ],
#     "2023.2": [
#         {"disc": "Cálculo II", "nota": 8.0},
#         {"disc": "Física II", "nota": 5.0}
#     ]
# }
def aprBySemester(json_data):
    grouped_data = {}
    for item in json_data["historico"]:
        if item["Situação"] == "APR":
            periodo = item["periodo"]
            if periodo not in grouped_data:
                grouped_data[periodo] = []
            grouped_data[periodo].append({"disc" : item["Disciplina"], "nota": item["Nota"]})
    return grouped_data

def rpvBySemester(json_data):
    grouped_data = {}
    for item in json_data["historico"]:
        if item["Situação"] != "APR":
            periodo = item["periodo"]
            if periodo not in grouped_data:
                grouped_data[periodo] = []
            grouped_data[periodo].append({"disc" : item["Disciplina"], "nota": item["Nota"]})
    return grouped_data

# Calcula o melhor e pior semestre com base na razão de aprovados
# e no total de disciplinas cursadas
# e atualiza os dados com essas informações
# Exemplo de saída:
# {
#     "generalStatistics": {
#         "bestSemester": {"period": "2023.1", "score": 0.75},
#         "worstSemester": {"period": "2023.2", "score": 0.25},
#         "scoreAvg": 0.5
#     }
#     "statisticsbySemester": {
#         "2023.1": {"pctApr": 0.75, "totalMat": 4},
#         "2023.2": {"pctApr": 0.25, "totalMat": 4}
#     }
# }
# A fórmula do score é: score = pctApr * sqrt(totalMat)
# onde pctApr é a razão de aprovados e totalMat é o total de disciplinas cursadas
# A média dos scores é calculada e adicionada ao dicionário
# de estatísticas gerais
def bestAndWorsePeriod(dados):
    # Inicializa valores
    bestPeriod = None
    worstPeriod = None
    bestScore = float("-inf")
    worstScore = float("inf")
    sumScore = 0 
    totalPeriods = 0

    # Calcula os scores dos semestres
    for period, stats in dados["statisticsBySemester"].items():
        score = stats["pctApr"] * math.sqrt(stats["totalMat"])  # Usa a nova fórmula
        # Atualiza melhor semestre
        if score > bestScore:
            bestScore = score
            bestPeriod = period
        # Atualiza pior semestre
        if score < worstScore:
            worstScore = score
            worstPeriod = period
        sumScore += score
        totalPeriods += 1
    # Atualiza os dados com os melhores e piores semestres
    #cria um indice de Score para o melhor e pior semestre e a média de todos os semestres
    dados["generalStatistics"] = {
        "bestSemester": {"period" : bestPeriod , "score" : round(bestScore , 4)}, 
        "worstSemester": {"period" : worstPeriod , "score" : round(worstScore , 4)},
        "scoreAvg" : round(sumScore / totalPeriods , 4)
    }

