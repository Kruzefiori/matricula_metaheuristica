#Esse é um projeto sendo desenvolvido para a disciplina XMCO03 - Metaheurísticas com o Prof. Dr. Rafael Frinhani
#Alunos responsáveis pelo desenvolvimento:
# - Victor Kruze Fiori
# - Augusto Lázaro

# from modules import interface
from modules import helper
from modules import pdfParser
from modules import printHelper
from modules import csvParser
from IPython.display import display
import pprint



def main():
    args = helper.argsParser()
    print(args)
    if args.run_cli_only == "y":
        try:
            structuredPdfData = pdfParser.parserPdf(args.dataset_name , args.update_json)
            availableDisciplines = csvParser.parseCSVavailableDisciplines(args.period)
            equivalences = csvParser.parseCSVequivalences()
            pprint.pprint(structuredPdfData)
            pprint.pprint(availableDisciplines)
            pprint.pprint(equivalences)
            #printHelper.printStructuredData(structuredPdfData)
            # Chama a função de recomendação
            if args.constructive == 'greedy':
                print("Executando o algoritmo guloso...")
                # Chama a função de recomendação gulosa
            elif args.constructive == 'ramdom':
                print("Executando o algoritmo aleatório...")
                # Chama a função de recomendação aleatória

            if args.refinement == 'dicipline':
                print("Executando o algoritmo de refinamento local...")
                # Chama a função de refinamento local
            elif args.refinement == 'score':
                print("Executando o algoritmo de refinamento por pontuação...")
                # Chama a função de refinamento por pontuação
            

            #graspManager(structuredPdfData)
        except Exception as e:
            print("Erro ao processar o arquivo PDF:", e)
            return
    else:
        # Executa a interface gráfica com as mesmas funções do CLI (não há impressão dos dados ainda)
        # interface.create_UI()
        print("Executando a interface gráfica...")


if __name__ == "__main__":
    main()
