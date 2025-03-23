import argparse
from modules import pdf_parser

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_name', required=True)
    args = parser.parse_args()
    pdf_parser.parser_pdf_to_json(args.dataset_name)


if __name__ == "__main__":
    main()
