import random
from copy import deepcopy

def build_discipline_schedule_map(catalog):
    schedule_map = {}
    for day, times in catalog['disciplinesByDayAndTime'].items():
        for time, disciplines in times.items():
            for disc in disciplines:
                if disc not in schedule_map:
                    schedule_map[disc] = set()
                schedule_map[disc].add((day, time))
    return schedule_map

def has_prerequisites(disc, current_solution, prerequisites, missing_disciplines):
    for prereq in prerequisites.get(disc, []):
        # Se o pré-requisito não está na solução nem nas pendentes, assume que já foi feito
        if prereq not in current_solution and prereq in missing_disciplines:
            return False
    return True

def disciplines_equivalences_map(equivalences):
    mapping = {}
    for eq in equivalences:
        disc = eq['discipline']
        eqs = eq['equivalences']
        mapping[disc] = eqs
    return mapping

def can_add_discipline(candidate_disc, current_solution, schedule_map, prerequisites, missing_disciplines):
    # Checar conflito de horários
    candidate_schedule = schedule_map.get(candidate_disc, set())
    for sol_disc in current_solution:
        sol_schedule = schedule_map.get(sol_disc, set())
        if candidate_schedule.intersection(sol_schedule):
            return False

    # Checar pré-requisitos
    return has_prerequisites(candidate_disc, current_solution, prerequisites, missing_disciplines)


def construct_solution(missing_disciplines, catalog, prerequisites, equivalences_map, schedule_map, k):
    solution = []
    candidates = set(missing_disciplines)

    while candidates:
        feasible_candidates = []

        for disc in candidates:
            equivs = equivalences_map.get(disc, [disc])

            for candidate_disc in equivs:
                if candidate_disc not in schedule_map:
                    continue  # Ignora equivalentes que não existem no catálogo

                if candidate_disc not in solution and can_add_discipline(candidate_disc, solution, schedule_map, prerequisites, missing_disciplines):
                    feasible_candidates.append(candidate_disc)
                    break  # Não precisa checar outras equivalências

        if not feasible_candidates:
            break

        rcl = feasible_candidates[:k] if len(feasible_candidates) >= k else feasible_candidates
        chosen = random.choice(rcl)
        solution.append(chosen)

        # Remove da lista de candidatos todas as equivalentes à escolhida
        to_remove = set()
        for disc in candidates:
            eqs = equivalences_map.get(disc, [disc])
            if chosen in eqs:
                to_remove.add(disc)

        candidates -= to_remove

    return solution

def score(solution, rare_disciplines):
    total = 0
    for disc in solution:
        if disc in rare_disciplines:
            total += 2  # Mais importante se é rara (só oferecida 1x no ano)
        else:
            total += 1  # Valor padrão
    return total



def local_search(solution, missing_disciplines, catalog, prerequisites, equivalences_map, schedule_map, rare_disciplines):
    best_solution = solution[:]
    best_score = score(best_solution, rare_disciplines)
    improved = True

    while improved:
        improved = False
        candidates = set(missing_disciplines) - set(best_solution)

        for cand in candidates:
            equivs = equivalences_map.get(cand, [cand])

            for candidate_disc in equivs:
                if candidate_disc not in schedule_map:
                    continue  # Ignorar equivalentes fora do catálogo
                if candidate_disc in best_solution:
                    continue

                conflict_disc = None
                candidate_schedule = schedule_map.get(candidate_disc, set())

                for sol_disc in best_solution:
                    sol_schedule = schedule_map.get(sol_disc, set())
                    if candidate_schedule.intersection(sol_schedule):
                        conflict_disc = sol_disc
                        break

                if conflict_disc:
                    new_solution = [d for d in best_solution if d != conflict_disc]
                    if can_add_discipline(candidate_disc, new_solution, schedule_map, prerequisites, missing_disciplines):
                        new_solution.append(candidate_disc)
                        if all(has_prerequisites(d, new_solution, prerequisites, missing_disciplines) for d in new_solution):
                            new_score = score(new_solution, rare_disciplines)
                            if new_score > best_score:
                                best_solution = new_solution
                                best_score = new_score
                                improved = True
                                break
                else:
                    if can_add_discipline(candidate_disc, best_solution, schedule_map, prerequisites, missing_disciplines):
                        new_solution = best_solution + [candidate_disc]
                        if all(has_prerequisites(d, new_solution, prerequisites, missing_disciplines) for d in new_solution):
                            new_score = score(new_solution, rare_disciplines)
                            if new_score > best_score:
                                best_solution = new_solution
                                best_score = new_score
                                improved = True
                                break

            if improved:
                break

    return best_solution



def quality_score(solution, catalog_current, catalog_previous):
    # Peso maior para disciplinas novas (não ofertadas no catálogo anterior)
    weight_new = 2
    weight_old = 1

    prev_disciplines = set()
    for day, times in catalog_previous['disciplinesByDayAndTime'].items():
        for time, discs in times.items():
            prev_disciplines.update(discs)

    curr_disciplines = set()
    for day, times in catalog_current['disciplinesByDayAndTime'].items():
        for time, discs in times.items():
            curr_disciplines.update(discs)

    score = 0
    for disc in solution:
        if disc not in curr_disciplines:
            # Disciplina não existe no catálogo atual, ignora
            continue
        if disc not in prev_disciplines:
            score += weight_new
        else:
            score += weight_old
    return score

def get_rare_disciplines(current_catalog, previous_catalog):
    current_set = set(current_catalog)
    previous_set = set(previous_catalog)
    
    rare = current_set - previous_set
    return rare


def grasp(missing_disciplines, catalog_current, prerequisites, catalog_previous=None, iterations=100, k=3, equivalences=None):
    equivalences_map = {}
    if equivalences:
        equivalences_map = disciplines_equivalences_map(equivalences)
    else:
        equivalences_map = {d: [d] for d in missing_disciplines}

    schedule_map = build_discipline_schedule_map(catalog_current)

    best_solution = []
    best_score = -1

    for _ in range(iterations):
        
        solution = construct_solution(missing_disciplines, catalog_current, prerequisites, equivalences_map, schedule_map, k)
        solution = local_search(solution, missing_disciplines, catalog_current, prerequisites, equivalences_map, schedule_map , get_rare_disciplines(catalog_current, catalog_previous))

        if catalog_previous is not None:
            scoreS =  score(solution, get_rare_disciplines(catalog_current, catalog_previous))# Se tiver catálogo anterior, usa a função de score
        else:
            scoreS = len(solution)  # Se não tiver catálogo anterior, usa tamanho da solução

        if scoreS > best_score:
            best_score = scoreS
            best_solution = solution

    return best_solution, score(solution, get_rare_disciplines(catalog_current, catalog_previous))
