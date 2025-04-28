#Esse é um projeto sendo desenvolvido para a disciplina XMCO03 - Metaheurísticas com o Prof. Dr. Rafael Frinhani
#Alunos responsáveis pelo desenvolvimento:
# - Victor Kruze Fiori
# - Augusto Lázaro

# from modules import interface
from modules import helper
from modules import pdfParser
from modules import printHelper
from modules.Grasp import graspManager 


def main():
    args = helper.argsParser()
    print(args)
    if args.run_cli_only == "y":
        try:
            structuredPdfData = pdfParser.parserPdf(args.dataset_name , args.update_json)
            #printHelper.printStructuredData(structuredPdfData)
            # Chama a função de recomendação
            graspManager(structuredPdfData)
        except Exception as e:
            print("Erro ao processar o arquivo PDF:", e)
            return
    else:
        # Executa a interface gráfica com as mesmas funções do CLI (não há impressão dos dados ainda)
        # interface.create_UI()
        print("Executando a interface gráfica...")


if __name__ == "__main__":
    main()
