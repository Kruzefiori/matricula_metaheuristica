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
        "--run_cli_only",
        type=str,
        help="O código deve ser executado apenas no terminal",
        default="y",
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
        help="Tipo de algoritmo construtivo a ser utilizado",
        default="greedy",
    )
    argsParser.add_argument(
        "--refinement",
        type=str,
        help="Tipo de algoritmo de refinamento a ser utilizado",
        default="dicipline",
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