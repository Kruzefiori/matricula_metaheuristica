import argparse
from modules import pdf

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_name', required=True)
    args = parser.parse_args()


    print(pdf.readPDFJSON(args))

if __name__ == "__main__":
    main()
