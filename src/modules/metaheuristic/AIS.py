# studentHistory:
# {
#   "aprBySemester": {
#     "<semestre>": [
#       {
#         "disc": "string",     // código da disciplina
#         "nota": "number"      // nota final
#       }
#     ]
#   },
#   "rpvBySemester": {
#     "<semestre>": [
#       {
#         "disc": "string",
#         "nota": "number|string" // pode ser nota numérica ou "--" para não realizado
#       }
#     ]
#   },
#   "statisticsBySemester": {
#     "<semestre>": {
#       "pctApr": "number",    // porcentagem de disciplinas aprovadas
#       "totalMat": "number"   // total de disciplinas matriculadas
#     }
#   },
#   "missingDisciplines": [
#     "string"                // disciplinas que deveriam ter sido cursadas, mas estão ausentes
#   ],
#   "generalStatistics": {
#     "bestSemester": {
#       "period": "string",
#       "score": "number"
#     },
#     "worstSemester": {
#       "period": "string",
#       "score": "number"
#     },
#     "scoreAvg": "number"
#   }
# }

# availableDisciplines:
# {
#   uniqueDisciplines: string[]; // Lista de códigos de disciplinas únicas

#   disciplinesByDayAndTime: {
#     [day: string]: {           // Ex: "Segunda-feira", "Terca-feira", etc.
#       [time: string]: string[]; // Ex: "10:10", "13:30", etc. → lista de códigos de disciplinas
#     };
#   };
# }

import random
import copy
from modules.metaheuristic import score

# Auxiliary functions

# Generates an initial population of solutions.
def generate_initial_population(studentHistory, allDisciplines, initialPopulation, maxRecommendationLength):
    missing_disciplines = set(studentHistory.get("missingDisciplines", []))
    available_disciplines = list(missing_disciplines.intersection(allDisciplines))

    all_solutions = []

    for _ in range(initialPopulation):
        if not available_disciplines:
            break

        num_disciplines = random.randint(1, min(maxRecommendationLength, len(available_disciplines)))
        solution = random.sample(available_disciplines, num_disciplines)
        all_solutions.append(solution)

    return all_solutions


def get_rare_disciplines(current_catalog, previous_catalog):
    current_set = set(current_catalog)
    previous_set = set(previous_catalog)
    return current_set - previous_set

def get_disciplines_intersection(rpvBySemester, other_list):
    all_disciplines = set()
    for semestre, disciplinas in rpvBySemester.items():
        for item in disciplinas:
            all_disciplines.add(item['disc'])

    resultado = list(all_disciplines.intersection(set(other_list)))
    return resultado

def count_prerequisite_frequency(prerequisites):
    freq = {}
    for disc_info in prerequisites.values():
        for prereq in disc_info.get('prerequisites', []):
            freq[prereq] = freq.get(prereq, 0) + 1
    return freq


# Evaluates the fitness of a solution based on various criteria.
def evaluate_fitness(solution, catalog_current, catalog_previous, rpv, missing_disciplines, prerequisites):
    rare = get_rare_disciplines(catalog_current, catalog_previous)
    reproved = get_disciplines_intersection(rpv, missing_disciplines) if rpv else []
    prereq_freq = count_prerequisite_frequency(prerequisites)
    fitness = score.score(solution=solution, rare_disciplines=rare, reproved=reproved, prereq_freq=prereq_freq)

    return fitness


# Gets the occupied slots from a solution based on the disciplines and their schedule.
def get_occupied_slots(solution, disciplinesByDayAndTime):
    occupied = set()
    for disc in solution:
        for day, times in disciplinesByDayAndTime.items():
            for time, disciplines_at_time in times.items():
                if disc in disciplines_at_time:
                    slot = f"{day}-{time}"
                    occupied.add(slot)
    return occupied

# Checks if adding a discipline would cause a conflict with the occupied slots.
def has_conflict(disc, occupied_slots, disciplinesByDayAndTime):
    for day, times in disciplinesByDayAndTime.items():
        for time, disciplines_at_time in times.items():
            if disc in disciplines_at_time:
                slot = f"{day}-{time}"
                if slot in occupied_slots:
                    return True
    return False

# Adds a discipline to the solution if it does not conflict with existing ones.
def add_disc_no_conflict(solution, candidate_pool, occupied_slots, disciplinesByDayAndTime):
    random.shuffle(candidate_pool)
    for disc in candidate_pool:
        if disc not in solution and not has_conflict(disc, occupied_slots, disciplinesByDayAndTime):
            return disc
    return None

# Mutates a solution by adding, removing, or replacing disciplines.
def mutate_solution(solution, studentHistory, offers, maxRecommendationLength):
    mutated = copy.deepcopy(solution)
    disciplinesByDayAndTime = offers.get('disciplinesByDayAndTime', {})
    occupied_slots = get_occupied_slots(mutated, disciplinesByDayAndTime)

    available = set(offers.get('uniqueDisciplines', []))
    missing = set(studentHistory.get('missingDisciplines', []))
    candidate_pool = list(available & missing)

    candidate_pool = [disc for disc in candidate_pool if disc not in mutated]
    if not candidate_pool:
        return mutated

    mutation_type = random.choice(["add", "remove", "replace"])

    if mutation_type == "add" and len(mutated) < maxRecommendationLength:
        new_disc = add_disc_no_conflict(mutated, candidate_pool, occupied_slots, disciplinesByDayAndTime)
        if new_disc:
            mutated.append(new_disc)

    elif mutation_type == "remove" and len(mutated) > 1:
        mutated.remove(random.choice(mutated))

    elif mutation_type == "replace" and candidate_pool:
        i = random.randint(0, len(mutated) - 1)
        new_disc = add_disc_no_conflict(mutated, candidate_pool, occupied_slots, disciplinesByDayAndTime)
        if new_disc:
            mutated[i] = new_disc

    return mutated

# Selects the best solutions from a list of all solutions based on their fitness scores.
def select_best_solutions(all_solutions, prerequisites, offers, neighborOffers, rpv, missing_disciplines, population_size):
    scored = [
        (sol, evaluate_fitness(sol, offers, neighborOffers, rpv, missing_disciplines, prerequisites))
        for sol in all_solutions
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    best_solutions = [sol for sol, _ in scored[:population_size]]
    return best_solutions


def similarity(sol1, sol2):
    set1, set2 = set(sol1), set(sol2)
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union else 1.0  # Similaridade de Jaccard


def suppress_similar_solutions(solutions, threshold=0.9):
    suppressed = []
    for sol in solutions:
        if all(similarity(sol, other) < threshold for other in suppressed):
            suppressed.append(sol)
    return suppressed


# --------------------------------------------------------------------------------------------------------------------
# Main function to run the AIS algorithm

def ais_algorithm(studentHistory, allDisciplines, offers, neighborOffers, prerequisites, maxRecommendationLength, initialPopulation=20, generations=100, clones_per_solution=3, diversification_rate=0.9, convergence_factor=0, suppress_factor=0.9):
    bestPeriod = studentHistory.get('generalStatistics', {}).get('bestSemester', {}).get('period', 'N/A')
    rpv = studentHistory.get('rpvBySemester')
    missing_disciplines = studentHistory.get('missingDisciplines', [])


    population = generate_initial_population(studentHistory, allDisciplines, initialPopulation, maxRecommendationLength)

    # Lista para armazenar as melhores soluções encontradas (e sua pontuação) a cada geração
    best_solutions_per_generation = []

    for gen in range(generations):
        # Avaliação
        scored_population = [(sol, evaluate_fitness(sol, offers, neighborOffers, rpv, missing_disciplines, prerequisites)) for sol in population]
        scored_population.sort(key=lambda x: x[1], reverse=True)

        # Seleção
        top_solutions = [sol for sol, score in scored_population[:initialPopulation // 2]]

        # Clonagem + Mutação
        clones = []
        for sol in top_solutions:
            for _ in range(clones_per_solution):
                mutated = mutate_solution(sol, studentHistory, offers, maxRecommendationLength)

                clones.append(mutated)

        # Diversificação: gera novas soluções aleatórias
        diversification_count = int(initialPopulation * diversification_rate) 
        new_random_solutions = generate_initial_population(studentHistory, allDisciplines, diversification_count, maxRecommendationLength)

        # Substituição: nova população é composta pelos melhores + clones + novos aleatórios
        all_solutions = top_solutions + clones + new_random_solutions

        # Aplica supressão à população antes de selecionar os melhores
        unique_solutions = suppress_similar_solutions(all_solutions, threshold=suppress_factor)
        population = select_best_solutions(unique_solutions, prerequisites, offers,neighborOffers, rpv, missing_disciplines, population_size=initialPopulation)


        # Armazena a melhor solução da geração atual
        best_solution = max(population, key=lambda sol: evaluate_fitness(sol, offers, neighborOffers, rpv, missing_disciplines, prerequisites))
        best_solutions_per_generation.append((best_solution, evaluate_fitness(best_solution, offers, neighborOffers, rpv, missing_disciplines, prerequisites)))

        # Critério de convergência (aplicado apenas se convergence_factor > 0)
        if convergence_factor > 0:
            # Calcula o tamanho da janela de convergência
            window_size = max(1, int(generations * convergence_factor))

            # Verifica se houve convergência nas últimas window_size gerações
            if len(best_solutions_per_generation) >= window_size:
              last_scores = [score for _, score in best_solutions_per_generation[-window_size:]]
              if max(last_scores) - min(last_scores) < 0.001:  # tolerância pequena
                break



    # Critério de parada: número de gerações
    best_solution = max(population, key=lambda sol: evaluate_fitness(sol, offers, neighborOffers, rpv, missing_disciplines, prerequisites))
    best_score = evaluate_fitness(best_solution, offers, neighborOffers, rpv, missing_disciplines, prerequisites)

    # Retorna a melhor solução encontrada, sua pontuação e o histórico das pontuações da melhor solução por geração
    best_scores_per_generation = [score for _, score in best_solutions_per_generation]
    return best_solution, best_score, best_scores_per_generation
