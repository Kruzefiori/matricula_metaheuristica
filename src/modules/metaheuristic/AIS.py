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

# Example of architecture of functions:
# def generate_initial_population(...)
# evaluate_fitness(solution, prerequisites, available_disc, neighbor_disc): ...
# def mutate_solution(solution, candidateDisciplines, constraints): ...
# def select_best_solutions(population, scores, n_best): ...
# def ais_algorithm(studentHistory, offers, initialPopulation=20, generations=10, clones_per_solution=3): ...

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

def evaluate_fitness(solution, prerequisites, available_disc, neighbor_disc):
    score = 0
    # Avalia a solução com base em critérios como:
    # - Tipo de disciplina (obrigatória, optativa)
    # - Duração (anual ou semestral)
    # - Dependências (disciplinas que esta destrava)
    # - Período ideal (simplificação - assumindo que todas são compatíveis)

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
    return score





# --------------------------------------------------------------------------------------------------------------------
# Main function to run the AIS algorithm














def mutate_solution(solution, candidateDisciplines, constraints): ...
def select_best_solutions(population, scores, n_best): ...


# Main function to run the AIS algorithm
def ais_algorithm(studentHistory, offers, neighborOffers, prerequisites, initialPopulation, generations, clones_per_solution):
      population = generate_initial_population(studentHistory, offers, initialPopulation)
    
      for gen in range(generations):
          scored_population = [(sol, evaluate_fitness(sol, prerequisites, offers, neighborOffers)) for sol in population]
          scored_population.sort(key=lambda x: x[1], reverse=True)
          for sol, score in scored_population:
              print(f"Solution: {sol}, Score: {score}")
          
          top_solutions = [sol for sol, score in scored_population[:initialPopulation // 2]]

      #     clones = []
      #     for sol in top_solutions:
      #         for _ in range(clones_per_solution):
      #             mutated = mutate_solution(sol, candidateDisciplines, constraints)
      #             clones.append(mutated)

      #     all_solutions = top_solutions + clones
      #     population = select_best_solutions(all_solutions, studentHistory, initialPopulation)

      # best_solution = max(population, key=lambda sol: evaluate_solution(sol, studentHistory))
      # return best_solution
