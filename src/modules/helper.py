import os
import json
import time
### Função para listar arquivos PDF na pasta datasets
def listFiles():
    try:
        return [f for f in os.listdir("./datasets") if f.lower().endswith(".pdf") and os.path.isfile(os.path.join("./datasets", f))]
    except FileNotFoundError:
        return []
    
### Função para definir os argumentos do script 
def argsParser():
    import argparse
    argsParser = argparse.ArgumentParser(description="Sistema de recomendação de matrícula")
    argsParser.add_argument(
        "--dataset_name",
        type=str,
        help="Nome do arquivo PDF a ser lido"
    )
    argsParser.add_argument(
        "--update_json",
        type=str,
        help="Atualiza o JSON se já existir",
        default="n",
    )
    argsParser.add_argument(
        "--period",
        type=str,
        help="Periodo de referência para o CSV",
        default="n",
    )
    argsParser.add_argument(
        "--constructive",
        type=str,
        help="Refinamento do resultado",
    )
    argsParser.add_argument(
        "--refinement",
        type=str,
        help="função de refinamento a ser utilizada",
    )
    argsParser.add_argument(
        "--mh",
        type=str,
        help="Metaheurística a ser utilizada",
        default="grasp",
    )
    argsParser.add_argument(
        "--k",
        type=str,
        help="k para o GRASP",
        default=3,
    )
    argsParser.add_argument(
        "--i",
        type=str,
        help="iterações para o GRASP",
        default=100
    )
    # args.initial_population
    # args.generations
    # args.clones_per_solution
    # args.diversification_rate
    argsParser.add_argument(
        "--initial_population",
        type=str,
        help="Tamanho da população inicial para o AIS",
        default=20
    )
    argsParser.add_argument(
        "--generations",
        type=str,
        help="Número de gerações para o AIS",
        default=100
    )
    argsParser.add_argument(
        "--clones_per_solution",
        type=str,
        help="Número de clones por solução para o AIS",
        default=3
    )
    argsParser.add_argument(
        "--diversification_rate",
        type=str,
        help="Taxa de diversificação para o AIS",
        default=0.2
    )
    argsParser.add_argument(
        "--convergence_factor",
        type=str,
        help="Limite de convergência para o AIS",
        default=0.01
    )
    argsParser.add_argument(
        "--supress_factor",
        type=str,
        help="Fator de supressão para o AIS",
        default=0.9
    )
    return argsParser.parse_args()

#checa se o Json já existe para não precisar criar novamente (é um processo demorado ler o pdf) 
def checkJsonExists(json_name):
    path = "./__dataset_output__/" + json_name + ".json"
    return os.path.exists(path)

def saveIntoTxt(name , data):
    with open("./" + name + "_last_execute_structured.txt", "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False))


def initiateTimer():
    return time.perf_counter()

def endTimer(start):
    end = time.perf_counter()
    print(f"Total execution time: {end - start:.6f} seconds")

def recommend_max_disciplines(statistics_by_semester, max_limit=7):
    if not statistics_by_semester:
        return 4  # default se não houver histórico

    sorted_semesters = sorted(statistics_by_semester.items())

    total_weight = 0
    weighted_sum = 0

    for i, (_, stats) in enumerate(sorted_semesters):
        total_mat = stats.get("totalMat", 0)
        pct_apr = stats.get("pctApr", 0)
        perf = total_mat * pct_apr

        weight = i + 1
        total_weight += weight
        weighted_sum += weight * perf

    avg_approved = weighted_sum / total_weight
    recommended = round(avg_approved)

    return max(2, min(recommended, max_limit))
