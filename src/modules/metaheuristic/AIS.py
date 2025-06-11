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

# Auxiliary functions

# Generates an initial population of solutions.
def generate_initial_population(studentHistory, offers, initialPopulation):
    bestPeriod = studentHistory.get('generalStatistics', {}).get('bestSemester', {}).get('period', 'N/A')
    maxRecommendationLength = studentHistory.get('statisticsBySemester', {}).get(bestPeriod, {}).get('totalMat', 0)
    missingDisciplines = studentHistory.get('missingDisciplines', [])
    availableDisciplines = offers.get('uniqueDisciplines', [])
    disciplinesByDayAndTime = offers.get('disciplinesByDayAndTime', {})

    # Disciplinas candidatas: pendentes e disponíveis
    candidateDisciplines = list(set(missingDisciplines) & set(availableDisciplines))
    
    all_solutions = []

    for _ in range(initialPopulation):
        # Embaralhar as candidatas
        random.shuffle(candidateDisciplines)

        solution = []
        occupied_slots = set()

        for disc in candidateDisciplines:
            # Verifica se a disciplina entra sem conflito
            conflict = False

            for day, times in disciplinesByDayAndTime.items():
                for time, disciplines_at_time in times.items():
                    if disc in disciplines_at_time:
                        slot = f"{day}-{time}"
                        if slot in occupied_slots:
                            conflict = True
                            break
                if conflict:
                    break

            if not conflict:
                solution.append(disc)

                # Marca os horários como ocupados
                for day, times in disciplinesByDayAndTime.items():
                    for time, disciplines_at_time in times.items():
                        if disc in disciplines_at_time:
                            slot = f"{day}-{time}"
                            occupied_slots.add(slot)

            # Respeita o limite máximo de disciplinas
            if len(solution) >= maxRecommendationLength:
                break

        all_solutions.append(solution)

    return all_solutions

# Evaluates the fitness of a solution based on various criteria.
def evaluate_fitness(solution, prerequisites, available_disc, neighbor_disc):
    score = 0

    # Avalia a solução com base em critérios como tipo de disciplina, duração, dependências e período ideal

    # Itera sobre as disciplinas na solução
    for disc in solution:
      # Tipo da disciplina
      disc_prerequisites = prerequisites.get(disc, {})
      discType = 1.0 if disc_prerequisites.get('isMandatory', False) else 0.5

      # Duração da disciplina (anual se oferecida em ambos semestres)
      is_annual = disc in available_disc.get('uniqueDisciplines', []) and disc in neighbor_disc.get('uniqueDisciplines', [])
      duration = 1.0 if is_annual else 0.5

      # Dependências (disciplinas que esta destrava)
      blocking = 0
      for other_disc, other_info in prerequisites.items():
          if disc in other_info.get('prerequisites', []):
              blocking += 0.2

      # Período ideal (simplificação - assumindo que todas são compatíveis)
      period = 0.5
      score += discType + duration - blocking + period

    # Retorna a pontuação total da solução
    return score

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
def select_best_solutions(all_solutions, prerequisites, offers, neighborOffers, population_size):
    # Avalia todas as soluções
    scored = [(sol, evaluate_fitness(sol, prerequisites, offers, neighborOffers)) for sol in all_solutions]
    
    # Ordena por score (maior primeiro)
    scored.sort(key=lambda x: x[1], reverse=True)

    # Retorna apenas as soluções, sem o score
    best_solutions = [sol for sol, score in scored[:population_size]]

    return best_solutions


# --------------------------------------------------------------------------------------------------------------------
# Main function to run the AIS algorithm
def ais_algorithm(studentHistory, offers, neighborOffers, prerequisites, initialPopulation, generations, clones_per_solution):
    """
    Runs the Artificial Immune System (AIS) algorithm to optimize course recommendations.
    The AIS algorithm follows these steps:
    * INITIALIZATION: Generate an initial population of solutions based on the student's history and available courses.
    * EVALUATION: Evaluate the fitness of each solution based on criteria such as course type, duration, dependencies, and ideal period.
    * SELECTION: Select the best solutions based on their fitness scores.
    * CLONING and MUTATION: For each selected solution, create clones with slight mutations to explore the solution space.
    ...
    """
    bestPeriod = studentHistory.get('generalStatistics', {}).get('bestSemester', {}).get('period', 'N/A')
    maxRecommendationLength = studentHistory.get('statisticsBySemester', {}).get(bestPeriod, {}).get('totalMat', 0)

    # INITIANIZATION
    population = generate_initial_population(studentHistory, offers, initialPopulation)
  
    for gen in range(generations):
        
        # EVALUATION
        scored_population = [(sol, evaluate_fitness(sol, prerequisites, offers, neighborOffers)) for sol in population]
        print(f"Generation {gen+1} scored population:")
        for i, (sol, score) in enumerate(scored_population):
            print(f"Solution {i+1}: {sol} - Score: {score}")
        
        # SELECTION
        scored_population.sort(key=lambda x: x[1], reverse=True)
        top_solutions = [sol for sol, score in scored_population[:initialPopulation // 2]] # Change this if you want a different selection size

        clones = []
        # CLONING and MUTATION
        for sol in top_solutions:
            for _ in range(clones_per_solution):
                mutated = mutate_solution(sol, studentHistory, offers, maxRecommendationLength)
                clones.append(mutated)

        all_solutions = top_solutions + clones
        print(f"All solutions after generation {gen+1}:")
        for i, sol in enumerate(all_solutions):
            print(f"Solution {i+1}: {sol} - Score: {evaluate_fitness(sol, prerequisites, offers, neighborOffers)}")
        
        # REPLACEMENT
        population = select_best_solutions(all_solutions, prerequisites, offers, neighborOffers, population_size=initialPopulation)

    best_solution = max(population, key=lambda sol: evaluate_fitness(sol, prerequisites, offers, neighborOffers))
    print(f"Best solution found: {best_solution} - Score: {evaluate_fitness(best_solution, prerequisites, offers, neighborOffers)}")
    return best_solution

