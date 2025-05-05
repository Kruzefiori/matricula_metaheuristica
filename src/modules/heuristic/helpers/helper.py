import json
from collections import defaultdict


dias_map = {
    "Segunda-feira": 1,
    "Terça-feira": 2,
    "Quarta-feira": 3,
    "Quinta-feira": 4,
    "Sexta-feira": 5
}


def addBlocks(disciplinas):
    blocks = defaultdict(int)

    # Conta quantas vezes cada disciplina aparece como pré-requisito
    for dados in disciplinas.values():
        for prereq in dados["prerequisites"]:
            blocks[prereq] += 1

    for cod, dados in disciplinas.items():
        dados["blocks"] = blocks.get(cod, 0)

    return disciplinas



def organizeData(availableDisciplines, neighborDisciplines):

    path = "./datasets/prerequisites/SIN_pre-requisitos.json"

    with open(path, "r", encoding="utf-8") as f:
        preReq = json.load(f)

    addBlocks(preReq)

    resultado = defaultdict(lambda: {"discipline": "", "time": defaultdict(list), "requisites": []})

    # Monta os dados básicos
    for dia, horarios in availableDisciplines["disciplinesByDayAndTime"].items():
        dia_num = dias_map[dia]
        for horario, disciplinas in horarios.items():
            for disc in disciplinas:
                resultado[disc]["discipline"] = disc
                resultado[disc]["time"][dia_num].append(horario)

    # Adiciona os pré-requisitos
    for cod_disc, dados in resultado.items():
        if cod_disc in preReq:
            dados["requisites"] = preReq[cod_disc]["prerequisites"]

    # Adiciona a flag oneByYear se necessário
    for disc in resultado.values():
        if disc['discipline'] not in neighborDisciplines["uniqueDisciplines"]:
            disc['oneByYear'] = True

    # Converte para lista formatada
    resultado_formatado = []
    for dados in resultado.values():
        item = {
            "discipline": dados["discipline"],
            "time": dict(dados["time"]),
            "requisites": dados["requisites"],
            "blocks": preReq[dados["discipline"]]["blocks"] if dados["discipline"] in preReq else 0
        }
        if "oneByYear" in dados:
            item["oneByYear"] = True
        resultado_formatado.append(item)

    return resultado_formatado