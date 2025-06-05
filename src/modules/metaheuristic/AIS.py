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

def ais_algorithm(studentHistory, offers):
    bestPeriod = studentHistory.get('generalStatistics', {}).get('bestSemester', {}).get('period', 'N/A')
    maxRecommendationLegth = studentHistory.get('statisticsBySemester', {}).get(bestPeriod, {}).get('totalMat', 0)
    missingDisciplines = set(studentHistory.get('missingDisciplines', []))
    availableDisciplines = set(offers.get('uniqueDisciplines', []))
    disciplinesByDayAndTime = offers.get('disciplinesByDayAndTime', {})

    # Disciplinas candidatas: pendentes e disponíveis
    candidate_disciplines = list(missingDisciplines & availableDisciplines)
    print("Disciplinas candidatas: ", candidate_disciplines)
    
    # Embaralha para construir soluções aleatórias
    random.shuffle(candidate_disciplines)
    
    solution = []  # Disciplinas recomendadas
    occupied_slots = set()  # Slots já ocupados: (dia, hora)

    for disc in candidate_disciplines:
        has_conflict = False
        
        # Verifica se a disciplina está alocada em algum dia e horário
        for day, times in disciplinesByDayAndTime.items():
            for time, disciplines in times.items():
                if disc in disciplines:
                    slot = (day, time)
                    if slot in occupied_slots:
                        has_conflict = True
                        break
            if has_conflict:
                break
        
        if not has_conflict:
            solution.append(disc)

            # Marca os slots ocupados por essa disciplina
            for day, times in disciplinesByDayAndTime.items():
                for time, disciplines in times.items():
                    if disc in disciplines:
                        occupied_slots.add((day, time))

        if len(solution) >= maxRecommendationLegth:
            break

    print("Solução recomendada: ", solution)
