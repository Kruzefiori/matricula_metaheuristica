import argparse
from modules import pdf
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_name', required=True)
    args = parser.parse_args()

    # Extrair as tabelas do PDF
    tables = pdf.getTablesFromPDF(args)
    # Processar as tabelas
    final_json_unformatted = pdf.processTables(tables)

    # Formatar o JSON
    final_json = json.dumps(json.loads(final_json_unformatted), indent=2, ensure_ascii=False)

    # Salvar o JSON, com o nome do dataset
    datasetName = str(args.dataset_name).replace('.pdf', '')
    with open(f"datasets/{datasetName}.json", "w") as f:
        f.write(final_json)
        print(f"JSON salvo em datasets/{datasetName}.json")

if __name__ == "__main__":
    main()
