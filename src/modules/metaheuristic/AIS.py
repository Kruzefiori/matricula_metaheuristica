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

def ais_algorithm(studentHistory, offers, initialPopulation):
    bestPeriod = studentHistory.get('generalStatistics', {}).get('bestSemester', {}).get('period', 'N/A')
    maxRecommendationLength = studentHistory.get('statisticsBySemester', {}).get(bestPeriod, {}).get('totalMat', 0)
    missingDisciplines = studentHistory.get('missingDisciplines', [])
    availableDisciplines = offers.get('uniqueDisciplines', [])
    disciplinesByDayAndTime = offers.get('disciplinesByDayAndTime', {})

    # Disciplinas candidatas: pendentes e disponíveis
    candidateDisciplines = list(set(missingDisciplines) & set(availableDisciplines))
    print(f"Disciplinas candidatas: {candidateDisciplines}")

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

    for i, solution in enumerate(all_solutions):
        print(f"Solução {i + 1}: {solution} (Tamanho: {len(solution)})")
        
    return all_solutions

