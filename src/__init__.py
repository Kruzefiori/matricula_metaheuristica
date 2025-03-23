import argparse
from modules import pdf
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_name', required=True)
    args = parser.parse_args()


    tables = pdf.getTablesFromPDF(args)
    final_json_unformatted = pdf.processTables(tables)

    # Formatar o JSON
    final_json = json.dumps(json.loads(final_json_unformatted), indent=2, ensure_ascii=False)

    # Salvar o JSON, com o nome do dataset
    with open(f"output/{args.dataset_name}.json", "w") as f:
        f.write(final_json)
        print(f"JSON salvo em output/{args.dataset_name}.json")
    

if __name__ == "__main__":
    main()
