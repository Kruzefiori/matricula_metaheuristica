import random
from copy import deepcopy

def recommend_max_disciplines(statistics_by_semester, max_limit=7):
    if not statistics_by_semester:
        return 4  # default se não houver histórico

    # Ordena os semestres cronologicamente
    sorted_semesters = sorted(statistics_by_semester.items())

    total_weight = 0
    weighted_sum = 0

    for i, (_, stats) in enumerate(sorted_semesters):
        total_mat = stats.get("totalMat", 0)
        pct_apr = stats.get("pctApr", 0)
        perf = total_mat * pct_apr

        # Peso maior para os semestres mais recentes
        weight = i + 1  # Ex: 1 para o mais antigo, 2, ..., N para o mais recente
        total_weight += weight
        weighted_sum += weight * perf

    # Média ponderada de disciplinas aprovadas por semestre
    avg_approved = weighted_sum / total_weight

    # Arredondar para cima para ser menos conservador
    recommended = round(avg_approved)

    return max(2, min(recommended, max_limit))  # Limita entre 2 e 7


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
    bidirectional_map = {}

    for group in equivalences:
        all_equivs = group["equivalences"] + [group["discipline"]]

        # Processa equivalências: transforma 'A + B' → ['A', 'B']
        processed = []
        for item in all_equivs:
            parts = [part.strip() for part in item.split('+')]
            if len(parts) > 1:
                processed.append(parts)
            else:
                processed.append(parts[0])

        # Para cada item no grupo, associe os demais como equivalentes
        for item in processed:
            key = tuple(item) if isinstance(item, list) else item
            if key not in bidirectional_map:
                bidirectional_map[key] = set()

            for other in processed:
                other_key = tuple(other) if isinstance(other, list) else other
                bidirectional_map[key].add(other_key)

    # Converte sets em listas para saída padronizada
    return {k: list(v) for k, v in bidirectional_map.items()}



def can_add_discipline(candidate_disc, current_solution, schedule_map, prerequisites, missing_disciplines):
    # Checar conflito de horários
    candidate_schedule = schedule_map.get(candidate_disc, set())
    for sol_disc in current_solution:
        sol_schedule = schedule_map.get(sol_disc, set())
        if candidate_schedule.intersection(sol_schedule):
            return False

    # Checar pré-requisitos
    return has_prerequisites(candidate_disc, current_solution, prerequisites, missing_disciplines)


def construct_solution(missing_disciplines, catalog, prerequisites, equivalences_map, schedule_map, k, max_disciplines):
    solution = []
    candidates = set(missing_disciplines)

    while candidates and len(solution) < max_disciplines:
        feasible_candidates = []

        for disc in candidates:
            equivs = equivalences_map.get(disc, [disc])

            for candidate_disc in equivs:
                if candidate_disc not in schedule_map:
                    continue

                if candidate_disc not in solution and can_add_discipline(candidate_disc, solution, schedule_map, prerequisites, missing_disciplines):
                    feasible_candidates.append(candidate_disc)
                    break

        if not feasible_candidates:
            break

        # Embaralha candidatos viáveis
        random.shuffle(feasible_candidates)
        n = len(feasible_candidates)

        if n < 2:
            slice_candidates = feasible_candidates
        else:
            i, j = sorted(random.sample(range(n), 2))  # dois pontos de corte
            slice_candidates = feasible_candidates[i:j+1]

        # Lista restrita dos melhores K candidatos nessa faixa (ordenado por raridade e prioridade)
        def sort_key(disc):
            return -int(disc in missing_disciplines)  # ou outro critério de prioridade

        slice_candidates.sort(key=sort_key)
        rcl = slice_candidates[:k] if len(slice_candidates) >= k else slice_candidates

        if not rcl:
            break

        chosen = random.choice(rcl)
        solution.append(chosen)

        to_remove = set()
        for disc in candidates:
            if chosen in equivalences_map.get(disc, [disc]):
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



def local_search(solution, missing_disciplines, catalog, prerequisites, equivalences_map, schedule_map, rare_disciplines, max_disciplines):
    best_solution = solution[:]
    best_score = score(best_solution, rare_disciplines)
    improved = True

    while improved:
        improved = False
        candidates = set(missing_disciplines) - set(best_solution)

        for cand in candidates:
            equivs = equivalences_map.get(cand, [cand])

            for candidate_disc in equivs:
                if candidate_disc not in schedule_map or candidate_disc in best_solution:
                    continue

                candidate_schedule = schedule_map.get(candidate_disc, set())
                conflict_disc = None

                for sol_disc in best_solution:
                    sol_schedule = schedule_map.get(sol_disc, set())
                    if candidate_schedule.intersection(sol_schedule):
                        conflict_disc = sol_disc
                        break

                # Troca com disciplina em conflito
                if conflict_disc:
                    new_solution = [d for d in best_solution if d != conflict_disc]
                    if len(new_solution) < max_disciplines and can_add_discipline(candidate_disc, new_solution, schedule_map, prerequisites, missing_disciplines):
                        new_solution.append(candidate_disc)
                        if all(has_prerequisites(d, new_solution, prerequisites, missing_disciplines) for d in new_solution):
                            new_score = score(new_solution, rare_disciplines)
                            if new_score > best_score:
                                best_solution = new_solution
                                best_score = new_score
                                improved = True
                                break
                else:
                    # Adiciona nova, mas só se respeitar limite
                    if len(best_solution) < max_disciplines and can_add_discipline(candidate_disc, best_solution, schedule_map, prerequisites, missing_disciplines):
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


def grasp(missing_disciplines, catalog_current, prerequisites, catalog_previous=None, iterations=100, k=3, equivalences=None, statistics_by_semester=None):
    equivalences_map = disciplines_equivalences_map(equivalences) if equivalences else {d: [d] for d in missing_disciplines}
    schedule_map = build_discipline_schedule_map(catalog_current)

    max_disciplines = recommend_max_disciplines(statistics_by_semester) if statistics_by_semester else 4
    best_solution = []
    best_score = -1

    for _ in range(iterations):
        solution = construct_solution(missing_disciplines, catalog_current, prerequisites, equivalences_map, schedule_map, k, max_disciplines)

        solution = local_search(
            solution,
            missing_disciplines,
            catalog_current,
            prerequisites,
            equivalences_map,
            schedule_map,
            get_rare_disciplines(catalog_current, catalog_previous),
            max_disciplines
        )

        if catalog_previous:
            scoreS = score(solution, get_rare_disciplines(catalog_current, catalog_previous))
        else:
            scoreS = len(solution)

        if scoreS > best_score:
            best_score = scoreS
            best_solution = solution

    return best_solution, best_score
