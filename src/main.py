#Esse é um projeto sendo desenvolvido para a disciplina XMCO03 - Metaheurísticas com o Prof. Dr. Rafael Frinhani
#Alunos responsáveis pelo desenvolvimento:
# - Victor Kruze Fiori
# - Augusto Lázaro

# from modules import interface
from modules import helper
from modules import pdfParser
from modules import printHelper
from modules.Grasp import graspManager
from modules.excelHandler import load_data, setRowAsHeader, setCollumnAsIndex, resetIndex, getCollumnNames, getRowNames, setCellValue, getCellValue, save_data
from IPython.display import display



def main():
    # args = helper.argsParser()
    # print(args)
    # if args.run_cli_only == "y":
    #     try:
    #         structuredPdfData = pdfParser.parserPdf(args.dataset_name , args.update_json)
    #         #printHelper.printStructuredData(structuredPdfData)
    #         # Chama a função de recomendação
    #         graspManager(structuredPdfData)
    #     except Exception as e:
    #         print("Erro ao processar o arquivo PDF:", e)
    #         return
    # else:
    #     # Executa a interface gráfica com as mesmas funções do CLI (não há impressão dos dados ainda)
    #     # interface.create_UI()
    #     print("Executando a interface gráfica...")

    # Load the data
  table = load_data('data/recomendacao-grade-horarios.xlsx', 'recomendacao1')
  display(table)

  # # Set the first row as header
  # table = setRowAsHeader(table, 0)
  # display(table)

  # Set the first column as index
  table = setCollumnAsIndex(table, 'Periodos')
  display(table)

  # Get column names
  columns = getCollumnNames(table)
  print("Column names:", columns)

  # Get row names
  rows = getRowNames(table)
  print("Row names:", rows)

  # Set a cell value
  table = setCellValue(table, '1M', 'sexta', 'metaheuristica')
  print("Updated table:")
  display(table)

  # Get a cell value
  value = getCellValue(table, '1M', 'sexta')
  print("Cell value:", value)

  # Save the data
  save_data(table, 'data/recomendacao-grade-horarios.xlsx', 'recomendacao1')


if __name__ == "__main__":
    main()
