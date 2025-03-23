import os

def listar_arquivos():
    try:
        return [f for f in os.listdir("./datasets") if f.lower().endswith(".pdf") and os.path.isfile(os.path.join("./datasets", f))]
    except FileNotFoundError:
        return []