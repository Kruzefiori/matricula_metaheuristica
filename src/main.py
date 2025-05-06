#Esse é um projeto sendo desenvolvido para a disciplina XMCO03 - Metaheurísticas com o Prof. Dr. Rafael Frinhani
#Alunos responsáveis pelo desenvolvimento:
# - Victor Kruze Fiori
# - Augusto Lázaro

# from modules import interface
import json
from modules import helper
from modules import pdfParser
from modules import printHelper
from modules import csvParser
from IPython.display import display
from modules.heuristic.constructive import greedyConstructive, randomizedConstructive
from modules.heuristic.refinement import refineByDisciplineAvailable, refineByEquivalence
import pprint



def main():
    args = helper.argsParser()
    print(args)
    if args.run_cli_only == "y":
        try:
            st = helper.initiateTimer()
            structuredPdfData = pdfParser.parserPdf(args.dataset_name , args.update_json)
            availableDisciplines = csvParser.parseCSVavailableDisciplines(args.period)
            neighborDisciplines = {}
            if args.period == "24.1" or args.period == "25.1":
                neighborDisciplines = csvParser.parseCSVavailableDisciplines("24.2")
            if args.period == "24.2":
                neighborDisciplines = csvParser.parseCSVavailableDisciplines("25.1")
            
            print("Estrutura do JSON criada com sucesso!")
            equivalences = csvParser.parseCSVequivalences()
            #pprint.pprint(structuredPdfData)
            #pprint.pprint(availableDisciplines)
            #pprint.pprint(equivalences)
            #printHelper.printStructuredData(structuredPdfData)
            # Chama a função de recomendação
            if args.constructive == 'greedy':
                print("Executando o algoritmo guloso...")
                # Chama a função de recomendação gulosa
                solutions  , formatedData = greedyConstructive.createGreedySolution(availableDisciplines , structuredPdfData , neighborDisciplines)
                #pprint.pprint(solutions)
                
            elif args.constructive == 'random':
                print("Executando o algoritmo aleatório...")
                # Chama a função de recomendação aleatória
                # obtém as disciplinas com pré-requisitos de dois arquivos JSON: um do curso de CCO e outro do curso de SIN
                # Carregar os arquivos JSON
                with open('datasets/prerequisites/SIN_pre-requisitos.json', 'r', encoding='utf-8') as f:
                    sin = json.load(f)

                with open('datasets/prerequisites/CCO_pre-requisitos.json', 'r', encoding='utf-8') as f:
                    cco = json.load(f)

                # Combinar as disciplinas (o último dicionário sobrescreve as chaves duplicadas)
                prerequisites = {**sin, **cco}

                # Chama a função de recomendação aleatória
                # randomizedConstructive.random_constructive(structuredPdfData, availableDisciplines, neighborDisciplines, prerequisites)
                randomBestSolution, randomBestScore, randomExcecutionTime = randomizedConstructive.random_constructive(structuredPdfData, availableDisciplines, neighborDisciplines, prerequisites)
                print('Melhor solução encontrada:', randomBestSolution)
                print('Pontuação da melhor solução:', randomBestScore)
                print('Tempo de execução:', randomExcecutionTime)
                

            if args.refinement == 'dicipline':
                print("Executando o algoritmo de refinamento local...")
                # Chama a função de refinamento local
                discRefinedSolutions, discRefinedScore, discExecutionTime = refineByDisciplineAvailable.local_search(randomBestSolution, randomBestScore, structuredPdfData, availableDisciplines, neighborDisciplines, prerequisites, 1000, 50)
                print('Melhor solução encontrada:', discRefinedSolutions)
                print('Pontuação da melhor solução:', discRefinedScore)
                print('Tempo de execução:', discExecutionTime)
            elif args.refinement == 'score':
                print("Executando o algoritmo de refinamento por pontuação...")
                # Chama a função de refinamento por pontuação
                refinedSolutions = refineByEquivalence.refinement(solutions, structuredPdfData['aprBySemester'], equivalences, formatedData)
                
                pprint.pprint(solutions)
                pprint.pprint(refinedSolutions)
                helper.endTimer(st)

            
            
            #graspManager(structuredPdfData)
        except Exception as e:
            print("Erro:", e)
            return
    else:
        # Executa a interface gráfica com as mesmas funções do CLI (não há impressão dos dados ainda)
        # interface.create_UI()
        print("Executando a interface gráfica...")


if __name__ == "__main__":
    main()
