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

def has_prerequisites(discipline, selected, prerequisites):
    if discipline not in prerequisites:
        return False
    prereqs = prerequisites[discipline].get('prerequisites', [])
    is_mandatory = prerequisites[discipline].get('isMandatory', True)
    if not is_mandatory:
        return True
    return all(pr in selected for pr in prereqs)

def disciplines_equivalences_map(equivalences):
    mapping = {}
    for eq in equivalences:
        disc = eq['discipline']
        eqs = eq['equivalences']
        mapping[disc] = eqs
    return mapping

def can_add_discipline(discipline, solution, schedule_map, prerequisites):
    # Verifica se disciplina existe no catálogo
    if discipline not in schedule_map:
        return False
    if not has_prerequisites(discipline, solution, prerequisites):
        return False
    disc_schedule = schedule_map.get(discipline, set())
    for sol_disc in solution:
        sol_schedule = schedule_map.get(sol_disc, set())
        if disc_schedule.intersection(sol_schedule):
            return False
    return True

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
                if candidate_disc not in solution and can_add_discipline(candidate_disc, solution, schedule_map, prerequisites):
                    feasible_candidates.append(candidate_disc)
                    break
        if not feasible_candidates:
            break
        rcl = feasible_candidates[:k] if len(feasible_candidates) >= k else feasible_candidates
        chosen = random.choice(rcl)
        solution.append(chosen)

        to_remove = set()
        for disc in candidates:
            eqs = equivalences_map.get(disc, [disc])
            if chosen in eqs:
                to_remove.add(disc)
        candidates -= to_remove

    return solution

def local_search(solution, missing_disciplines, catalog, prerequisites, equivalences_map, schedule_map):
    best_solution = solution[:]
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
                    if can_add_discipline(candidate_disc, new_solution, schedule_map, prerequisites):
                        new_solution.append(candidate_disc)
                        if all(has_prerequisites(d, new_solution, prerequisites) for d in new_solution):
                            if len(new_solution) > len(best_solution):
                                best_solution = new_solution
                                improved = True
                                break
                else:
                    if can_add_discipline(candidate_disc, best_solution, schedule_map, prerequisites):
                        new_solution = best_solution + [candidate_disc]
                        if all(has_prerequisites(d, new_solution, prerequisites) for d in new_solution):
                            best_solution = new_solution
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
        solution = local_search(solution, missing_disciplines, catalog_current, prerequisites, equivalences_map, schedule_map)

        if catalog_previous is not None:
            score = quality_score(solution, catalog_current, catalog_previous)
        else:
            score = len(solution)  # Se não tiver catálogo anterior, usa tamanho da solução

        if score > best_score:
            best_score = score
            best_solution = solution

    return best_solution, best_score
