#Esse é um projeto sendo desenvolvido para a disciplina XMCO03 - Metaheurísticas com o Prof. Dr. Rafael Frinhani
#Alunos responsáveis pelo desenvolvimento:
# - Victor Kruze Fiori
# - Augusto Lázaro

import json
from modules import helper
from modules import pdfParser
from modules import printHelper
from modules import csvParser
from modules.metaheuristic import grasp
from modules.metaheuristic import AIS
from IPython.display import display
import pprint



def main():
    args = helper.argsParser()
    print(args)
    st = helper.initiateTimer()
    structuredPdfData = pdfParser.parserPdf(args.dataset_name , args.update_json)
    availableDisciplines = csvParser.parseCSVavailableDisciplines(args.period)
    neighborDisciplines = {}
    if args.period == "24.1" or args.period == "25.1":
        neighborDisciplines = csvParser.parseCSVavailableDisciplines("24.2")
    if args.period == "24.2":
        neighborDisciplines = csvParser.parseCSVavailableDisciplines("25.1")
    with open('datasets/prerequisites/SIN_pre-requisitos.json', 'r', encoding='utf-8') as f:
        sin = json.load(f)
    with open('datasets/prerequisites/CCO_pre-requisitos.json', 'r', encoding='utf-8') as f:
        cco = json.load(f)
    # Combinar as disciplinas (o último dicionário sobrescreve as chaves duplicadas)
    prerequisites = {**sin, **cco}
    equivalences = csvParser.parseCSVequivalences()
    max_disciplines = helper.recommend_max_disciplines(structuredPdfData.get('statisticsBySemester', {}))
    # Chama a função de recomendação escolhida
    if args.mh == 'grasp':  # Se o usuário escolheu GRASP
        #python src/main.py --period "25.1" --mh "grasp" --update_json "y" --dataset_name "historico_SIN-5"
        print("Executando o algoritmo Grasp...")
        # Extrair missing disciplines e histórico do structuredPdfData
        #pprint.pprint(prerequisites)

        missing_disciplines = structuredPdfData.get('missingDisciplines', [])       
        best_solution, best_score = grasp.grasp(
            missing_disciplines,
            availableDisciplines,
            prerequisites,
            catalog_previous=neighborDisciplines,  # catálogo anterior para priorizar disciplinas unicas no ano
            iterations=int(args.i),
            k=int(args.k),
            equivalences=equivalences,
            max_disciplines = max_disciplines,
            rpv = structuredPdfData.get('rpvBySemester')
        )
        print("Melhor solução encontrada:")
        pprint.pprint(best_solution)
        print(f"Pontuação: {best_score}")
        helper.endTimer(st)
        return
    if args.mh == 'AIS':
        print("Executando o algoritmo AIS...")

        # best_solution, best_score = AIS.ais_algorithm(...)
        # print("Melhor solução encontrada:")
        # pprint.pprint(best_solution)
        # print(f"Pontuação: {best_score}")
        initialPopulation = 5
        generations = 1
        clones_per_solution = 3
        AIS.ais_algorithm(structuredPdfData, availableDisciplines, neighborDisciplines, prerequisites, initialPopulation, generations, clones_per_solution)
        helper.endTimer(st)


if __name__ == "__main__":
    main()



#Old code for reference, not used in the current implementation:
# print("Executando o algoritmo guloso...")
#                 # Chama a função de recomendação gulosa
#                 solutions  , formatedData = greedyConstructive.createGreedySolution(availableDisciplines , structuredPdfData , neighborDisciplines)
#                 #pprint.pprint(solutions)
                
#             elif args.constructive == 'random':
#                 print("Executando o algoritmo aleatório...")
#                 # Chama a função de recomendação aleatória
#                 # obtém as disciplinas com pré-requisitos de dois arquivos JSON: um do curso de CCO e outro do curso de SIN
#                 # Carregar os arquivos JSON
#                 with open('datasets/prerequisites/SIN_pre-requisitos.json', 'r', encoding='utf-8') as f:
#                     sin = json.load(f)

#                 with open('datasets/prerequisites/CCO_pre-requisitos.json', 'r', encoding='utf-8') as f:
#                     cco = json.load(f)

#                 # Combinar as disciplinas (o último dicionário sobrescreve as chaves duplicadas)
#                 prerequisites = {**sin, **cco}

#                 # Chama a função de recomendação aleatória
#                 # randomizedConstructive.random_constructive(structuredPdfData, availableDisciplines, neighborDisciplines, prerequisites)
#                 randomBestSolution, randomBestScore, randomExcecutionTime = randomizedConstructive.random_constructive(structuredPdfData, availableDisciplines, neighborDisciplines, prerequisites)
#                 print('Melhor solução encontrada:', randomBestSolution)
#                 print('Pontuação da melhor solução:', randomBestScore)
#                 print('Tempo de execução:', randomExcecutionTime)
                

#             if args.refinement == 'dicipline':
#                 print("Executando o algoritmo de refinamento local...")
#                 # Chama a função de refinamento local
#                 discRefinedSolutions, discRefinedScore, discExecutionTime = refineByDisciplineAvailable.local_search(randomBestSolution, randomBestScore, structuredPdfData, availableDisciplines, neighborDisciplines, prerequisites, 1000, 50)
#                 print('Melhor solução encontrada:', discRefinedSolutions)
#                 print('Pontuação da melhor solução:', discRefinedScore)
#                 print('Tempo de execução:', discExecutionTime)
#             elif args.refinement == 'score':
#                 print("Executando o algoritmo de refinamento por pontuação...")
#                 # Chama a função de refinamento por pontuação
#                 refinedSolutions = refineByEquivalence.refinement(solutions, structuredPdfData['aprBySemester'], equivalences, formatedData)
                
#                 pprint.pprint(solutions)
#                 pprint.pprint(refinedSolutions)
#                 helper.endTimer(st)
