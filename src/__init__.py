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

    # Salvar o JSON
    with open("final.json", "w") as outfile:
        outfile.write(final_json)

    

if __name__ == "__main__":
    main()
