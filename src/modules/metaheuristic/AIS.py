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

# equivalences:
  # [
  #   {
  #     "discipline": "nome_da_disciplina",
  #     "equivalences": [
  #       "nome_da_equivalencia_1",
  #       "nome_da_equivalencia_2",
  #       ...
  #     ]
  #   },
  #   ...
  # ]

import random
import copy
from modules.metaheuristic import score

# Auxiliary functions

# Gets all the approved disciplines from the student's history.
def get_approved_disciplines(studentHistory):
    aprBySemester = studentHistory.get('aprBySemester', {})
    allApproved = set()
    for semester, disciplines in aprBySemester.items():
        for item in disciplines:
            allApproved.add(item['disc'])
    return list(allApproved)




# Generates an initial population of solutions.
def generate_initial_population(allDisciplines, initialPopulation, maxRecommendationLength):

  all_solutions = []

  for _ in range(initialPopulation):
      # Define aleatoriamente quantas disciplinas essa solução terá (entre 1 e o máximo)
      num_disciplines = random.randint(1, maxRecommendationLength)

      # Escolhe disciplinas aleatórias, sem se preocupar com conflitos ou restrições
      solution = random.sample(allDisciplines, min(num_disciplines, len(allDisciplines)))

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
def evaluate_fitness(solution, catalog_current, catalog_previous, rpv, missing_disciplines, prerequisites, approved_disciplines, equivalences):
    # Antes de calcular a pontuação, verificar as situções que tornam cada disciplina não factível e penalizar a pontuação:
    # 1. Verificar se a disciplina foi ofertada no período atual.
    # 2. Verificar se a disciplina está entre as disciplinas pendentes do aluno.
    # 3. Verificar se há conflitos de horário com as outras disciplinas já selecionadas na solução.
    # 4. Verificar se a o aluno já cursou todas as disciplinas pré-requisitas da disciplina.
    # 5. Verificar se a disciplina é uma das equivalências. Se for, verificar se a disciplina equivalente é uma das pendentes do aluno.
  
    penalty = 0
    # 1. Verifica se todas as disciplinas estão no catálogo atual
    for disc in solution:
        if disc not in catalog_current.get('uniqueDisciplines', []):
            penalty += 1  # Penaliza se a disciplina não está no catálogo atual

    # 2. Verifica se todas as disciplinas estão entre as pendentes do aluno
    for disc in solution:
        if disc not in missing_disciplines:
            penalty += 1 # Penaliza se a disciplina não está entre as pendentes do aluno

    # 3. Verifica conflitos de horário
    disciplinesByDayAndTime = catalog_current.get('disciplinesByDayAndTime', {})
    occupied_slots = get_occupied_slots(solution, disciplinesByDayAndTime)
    for disc in solution:
        if has_conflict(disc, occupied_slots, disciplinesByDayAndTime):
            penalty += 1 # Penaliza se há conflito de horário com outras disciplinas na solução

    # 4. Verifica se o aluno já cursou todas as disciplinas pré-requisitas
    for disc in solution:
        prereqs = prerequisites.get(disc, {}).get('prerequisites', [])
        if not all(prereq in approved_disciplines for prereq in prereqs):
            penalty += 1  # Penaliza se o aluno não cursou todas as pré-requisitas
    
    # 5. Verifica se a disciplina é uma equivalência e se a equivalente está entre as pendentes
    for disc in solution:
        if disc in equivalences:
            for equiv in equivalences[disc]:
                if equiv not in missing_disciplines:
                    penalty += 1

    rare = get_rare_disciplines(catalog_current, catalog_previous)
    reproved = get_disciplines_intersection(rpv, missing_disciplines) if rpv else []
    prereq_freq = count_prerequisite_frequency(prerequisites)
    fitness = score.score(solution=solution, rare_disciplines=rare, reproved=reproved, prereq_freq=prereq_freq)

    # Subtrai a penalidade da pontuação total
    fitness -= penalty
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
def select_best_solutions(all_solutions, prerequisites, offers, neighborOffers, rpv, missing_disciplines, population_size, approved_disciplines, equivalences):
    scored = [
        (sol, evaluate_fitness(sol, offers, neighborOffers, rpv, missing_disciplines, prerequisites, approved_disciplines, equivalences))
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

def ais_algorithm(studentHistory, equivalences, offers, neighborOffers, prerequisites, maxRecommendationLength, initialPopulation=20, generations=100, clones_per_solution=3, diversification_rate=0.9, convergence_factor=0, suppress_factor=0.9):
    rpv = studentHistory.get('rpvBySemester')
    missing_disciplines = studentHistory.get('missingDisciplines', [])
    approved_disciplines = get_approved_disciplines(studentHistory)
    offeredDisciplines = offers.get('uniqueDisciplines', [])

    population = generate_initial_population(offeredDisciplines, initialPopulation, maxRecommendationLength)

    # Lista para armazenar as melhores soluções encontradas (e sua pontuação) a cada geração
    best_solutions_per_generation = []

    for gen in range(generations):
        # Avaliação
        scored_population = [(sol, evaluate_fitness(sol, offers, neighborOffers, rpv, missing_disciplines, prerequisites, approved_disciplines, equivalences)) for sol in population]
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
        new_random_solutions = generate_initial_population(offeredDisciplines, diversification_count, maxRecommendationLength)

        # Substituição: nova população é composta pelos melhores + clones + novos aleatórios
        all_solutions = top_solutions + clones + new_random_solutions

        # Aplica supressão à população antes de selecionar os melhores
        unique_solutions = suppress_similar_solutions(all_solutions, threshold=suppress_factor)
        population = select_best_solutions(unique_solutions, prerequisites, offers, neighborOffers, rpv, missing_disciplines, initialPopulation, approved_disciplines, equivalences)


        # Armazena a melhor solução da geração atual
        best_solution = max(population, key=lambda sol: evaluate_fitness(sol, offers, neighborOffers, rpv, missing_disciplines, prerequisites, approved_disciplines, equivalences))
        best_solutions_per_generation.append((best_solution, evaluate_fitness(best_solution, offers, neighborOffers, rpv, missing_disciplines, prerequisites, approved_disciplines, equivalences)))

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
    best_solution = max(population, key=lambda sol: evaluate_fitness(sol, offers, neighborOffers, rpv, missing_disciplines, prerequisites, approved_disciplines, equivalences))
    best_score = evaluate_fitness(best_solution, offers, neighborOffers, rpv, missing_disciplines, prerequisites, approved_disciplines, equivalences)


    return best_solution, best_score
