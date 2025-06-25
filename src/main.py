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
from modules.heuristic.constructive import greedyConstructive , randomizedConstructive
from modules.heuristic.refinement import refineByDisciplineAvailable , refineByEquivalence
from IPython.display import display
import pprint
import matplotlib.pyplot as plt

import json

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

    if args.constructive == 'greedy':
        print("Executando o algoritmo guloso...")
        # Chama a função de recomendação gulosa
        solutions  , formatedData = greedyConstructive.createGreedySolution(availableDisciplines , structuredPdfData , neighborDisciplines)
        pprint.pprint(solutions[0])
        
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
        

    if args.refinement == 'discipline':
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

        initialPopulation = int(args.initial_population)
        generations = int(args.generations)
        clones_per_solution = int(args.clones_per_solution)
        diversification_rate = float(args.diversification_rate)
        convergence_factor = float(args.convergence_factor)
        supress_factor = float(args.supress_factor)

        best_solution_AIS, best_score_AIS = AIS.ais_algorithm(
            studentHistory=structuredPdfData,
            equivalences=equivalences,
            offers=availableDisciplines,
            neighborOffers=neighborDisciplines,
            prerequisites=prerequisites,
            maxRecommendationLength= max_disciplines,
            initialPopulation=initialPopulation,
            generations=generations,
            clones_per_solution=clones_per_solution,
            diversification_rate=diversification_rate,
            convergence_factor=convergence_factor,
            suppress_factor=supress_factor
        )
        helper.endTimer(st)
        
        print("Melhor solução encontrada:")
        pprint.pprint(best_solution_AIS)
        print(f"Score: {best_score_AIS}")

        # # Número de iterações (eixo x)
        # iterations = list(range(1, len(best_scores_per_generation) + 1))

        # # Criando o gráfico
        # plt.plot(iterations, best_scores_per_generation, marker='o', linestyle='-', color='blue')
        # plt.title('Progresso do Score ao Longo das gerações')
        # plt.xlabel('Iteração')
        # plt.ylabel('Score')
        # plt.grid(True)
        # plt.tight_layout()

        # # Exibe o gráfico
        # plt.show()
        
        # Adicionar os resultados ao arquivo de texto AIS_results.txt. Para cada nova execução, os resultados serão adicionados ao final do arquivo.
        # with open("AIS_results.txt", "a", encoding="utf-8") as f:
        #     f.write(f"Dataset: {args.dataset_name}\n\n")
        #     f.write(f"Parâmetros utilizados: População Inicial:\n{initialPopulation}\n Gerações: {generations}\n Clones por Solução: {clones_per_solution}\n Taxa de Diversificação: {diversification_rate}\n Limite de Convergência: {convergence_factor}\n Fator de Supressão: {supress_factor}\n")
        #     f.write("Melhor solução encontrada pelo AIS: ")
        #     f.write(f"{best_solution_AIS}\n")
        #     f.write(f"Pontuação: {best_score_AIS}\n")
        #     f.write("Histórico de pontuações por geração: [")
        #     for i, score in enumerate(best_scores_per_generation):
        #         # f.write(f"{score:.2f}, ")
        #         if i == len(best_scores_per_generation) - 1:
        #             f.write(f"{score:.2f}")
        #         else:
        #             f.write(f"{score:.2f}, ")
        #     f.write("]\n")
        #     f.write("-" * 50 + "\n\n")

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
