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