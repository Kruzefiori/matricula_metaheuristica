import random
from copy import deepcopy
from modules.metaheuristic.score import score

def recommend_max_disciplines(statistics_by_semester, max_limit=7):
    if not statistics_by_semester:
        return 4  # default se não houver histórico

    sorted_semesters = sorted(statistics_by_semester.items())

    total_weight = 0
    weighted_sum = 0

    for i, (_, stats) in enumerate(sorted_semesters):
        total_mat = stats.get("totalMat", 0)
        pct_apr = stats.get("pctApr", 0)
        perf = total_mat * pct_apr

        weight = i + 1
        total_weight += weight
        weighted_sum += weight * perf

    avg_approved = weighted_sum / total_weight
    recommended = round(avg_approved)

    return max(2, min(recommended, max_limit))


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
    for prereq in prerequisites.get(disc, {}).get('prerequisites', []):
        if prereq not in current_solution and prereq in missing_disciplines:
            return False
    return True


def disciplines_equivalences_map(equivalences):
    bidirectional_map = {}

    for group in equivalences:
        all_equivs = group["equivalences"] + [group["discipline"]]

        processed = []
        for item in all_equivs:
            parts = [part.strip() for part in item.split('+')]
            if len(parts) > 1:
                processed.append(parts)
            else:
                processed.append(parts[0])

        for item in processed:
            key = tuple(item) if isinstance(item, list) else item
            if key not in bidirectional_map:
                bidirectional_map[key] = set()

            for other in processed:
                other_key = tuple(other) if isinstance(other, list) else other
                bidirectional_map[key].add(other_key)

    return {k: list(v) for k, v in bidirectional_map.items()}


def can_add_discipline(candidate_disc, current_solution, schedule_map, prerequisites, missing_disciplines):
    candidate_schedule = schedule_map.get(candidate_disc, set())
    for sol_disc in current_solution:
        sol_schedule = schedule_map.get(sol_disc, set())
        if candidate_schedule.intersection(sol_schedule):
            return False
    return has_prerequisites(candidate_disc, current_solution, prerequisites, missing_disciplines)


def construct_solution(missing_disciplines, catalog, prerequisites, equivalences_map, schedule_map, k, max_disciplines, rare_disciplines=None, reproved=None, prereq_freq=None):
    solution = []
    candidates = set(missing_disciplines)

    while candidates:
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

        random.shuffle(feasible_candidates)
        n = len(feasible_candidates)

        if n < 2:
            slice_candidates = feasible_candidates
        else:
            i, j = sorted(random.sample(range(n), 2))
            slice_candidates = feasible_candidates[i:j+1]

        def sort_key(disc):
            peso = 0
            if rare_disciplines and disc in rare_disciplines:
                peso += 1
            if reproved and disc in reproved:
                peso += 2
            if prereq_freq:
                peso += prereq_freq.get(disc, 0)
            return -peso

        slice_candidates.sort(key=sort_key)
        rcl = slice_candidates[:k] if len(slice_candidates) >= k else slice_candidates

        if not rcl:
            break

        chosen = random.choice(rcl)

        if len(solution) < max_disciplines:
            solution.append(chosen)
        else:
            # Tentativa de substituir alguma disciplina na solução para melhorar o score
            current_score = score(solution, rare_disciplines or set(), reproved or [], prereq_freq or {})
            improved = False

            for idx, existing_disc in enumerate(solution):
                temp_solution = solution[:idx] + solution[idx+1:] + [chosen]
                if all(has_prerequisites(d, temp_solution, prerequisites, missing_disciplines) for d in temp_solution):
                    if not any(schedule_map[chosen].intersection(schedule_map[d]) for d in temp_solution if d != chosen):
                        new_score = score(temp_solution, rare_disciplines or set(), reproved or [], prereq_freq or {})
                        if new_score > current_score:
                            solution = temp_solution
                            improved = True
                            break
            if not improved:
                # Nenhuma substituição melhora a solução, termina
                break

        to_remove = set()
        for disc in candidates:
            if chosen in equivalences_map.get(disc, [disc]):
                to_remove.add(disc)

        candidates -= to_remove

    return solution[:max_disciplines]


def local_search(solution, missing_disciplines, catalog, prerequisites, equivalences_map, schedule_map, rare_disciplines, max_disciplines, reproved, prereq_freq):
    best_solution = solution[:]
    best_score = score(best_solution, rare_disciplines, reproved, prereq_freq)
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

                if conflict_disc:
                    new_solution = [d for d in best_solution if d != conflict_disc]
                    # Aqui sempre tenta substituir se melhorar score
                    if can_add_discipline(candidate_disc, new_solution, schedule_map, prerequisites, missing_disciplines):
                        new_solution.append(candidate_disc)
                        if all(has_prerequisites(d, new_solution, prerequisites, missing_disciplines) for d in new_solution):
                            new_score = score(new_solution, rare_disciplines, reproved, prereq_freq)
                            if new_score > best_score:
                                best_solution = new_solution
                                best_score = new_score
                                improved = True
                                break
                else:
                    # Se já chegou ao limite, tenta substituir alguma para melhorar score
                    if len(best_solution) < max_disciplines:
                        if can_add_discipline(candidate_disc, best_solution, schedule_map, prerequisites, missing_disciplines):
                            new_solution = best_solution + [candidate_disc]
                            if all(has_prerequisites(d, new_solution, prerequisites, missing_disciplines) for d in new_solution):
                                new_score = score(new_solution, rare_disciplines, reproved, prereq_freq)
                                if new_score > best_score:
                                    best_solution = new_solution
                                    best_score = new_score
                                    improved = True
                                    break
                    else:
                        # Tenta substituir para melhorar score
                        current_score = best_score
                        improved_local = False
                        for idx, existing_disc in enumerate(best_solution):
                            temp_solution = best_solution[:idx] + best_solution[idx+1:] + [candidate_disc]
                            if all(has_prerequisites(d, temp_solution, prerequisites, missing_disciplines) for d in temp_solution):
                                # Verifica conflito de horário
                                conflict = False
                                for d in temp_solution:
                                    if d == candidate_disc:
                                        continue
                                    if schedule_map[candidate_disc].intersection(schedule_map[d]):
                                        conflict = True
                                        break
                                if not conflict:
                                    new_score = score(temp_solution, rare_disciplines, reproved, prereq_freq)
                                    if new_score > current_score:
                                        best_solution = temp_solution
                                        best_score = new_score
                                        improved = True
                                        improved_local = True
                                        break
                        if improved_local:
                            break

            if improved:
                break

    return best_solution


def count_prerequisite_frequency(prerequisites):
    freq = {}
    for disc_info in prerequisites.values():
        for prereq in disc_info.get('prerequisites', []):
            freq[prereq] = freq.get(prereq, 0) + 1
    return freq


def get_rare_disciplines(current_catalog, previous_catalog):
    current_set = set(current_catalog)
    previous_set = set(previous_catalog)
    return current_set - previous_set


def path_relinking(sol1, sol2, score_func, score_args, reproved, rare_disciplines):
    best_solution = sol1[:]
    best_score = score_func(best_solution, rare_disciplines, reproved, score_args['prereq_freq'])

    target_solution = sol2[:]
    current_solution = sol1[:]

    diff = [d for d in target_solution if d not in current_solution]

    for disc in diff:
        new_solution = current_solution[:]

        conflict_disc = None
        candidate_schedule = score_args['schedule_map'].get(disc, set())

        for sol_disc in new_solution:
            sol_schedule = score_args['schedule_map'].get(sol_disc, set())
            if candidate_schedule.intersection(sol_schedule):
                conflict_disc = sol_disc
                break

        if conflict_disc:
            new_solution.remove(conflict_disc)

        if can_add_discipline(disc, new_solution, score_args['schedule_map'], score_args['prerequisites'], score_args['missing_disciplines']):
            new_solution.append(disc)
            if all(has_prerequisites(d, new_solution, score_args['prerequisites'], score_args['missing_disciplines']) for d in new_solution):
                new_score = score_func(new_solution, rare_disciplines, reproved, score_args['prereq_freq'])
                if new_score > best_score:
                    best_solution = new_solution
                    best_score = new_score
                    current_solution = new_solution

    # Corta solução para garantir limite máximo
    if len(best_solution) > score_args['max_disciplines']:
        best_solution = best_solution[:score_args['max_disciplines']]

    return best_solution


def get_disciplines_intersection(rpvBySemester, other_list):
    all_disciplines = set()
    for semestre, disciplinas in rpvBySemester.items():
        for item in disciplinas:
            all_disciplines.add(item['disc'])

    resultado = list(all_disciplines.intersection(set(other_list)))
    return resultado


def grasp(missing_disciplines, catalog_current, prerequisites, catalog_previous=None, iterations=100, k=3, equivalences=None, max_disciplines=4, rpv=None):
    equivalences_map = disciplines_equivalences_map(equivalences) if equivalences else {d: [d] for d in missing_disciplines}
    schedule_map = build_discipline_schedule_map(catalog_current)

    max_disciplines
    print(f"Recomendando até {max_disciplines} disciplinas com base no histórico.")
    reproved = get_disciplines_intersection(rpv, missing_disciplines) if rpv else []
    prereq_freq = count_prerequisite_frequency(prerequisites)

    best_solution = []
    best_score = -1

    elite_solutions = []
    elite_limit = 5

    rare = get_rare_disciplines(catalog_current, catalog_previous)

    score_args = {
        'prereq_freq': prereq_freq,
        'schedule_map': schedule_map,
        'prerequisites': prerequisites,
        'missing_disciplines': missing_disciplines,
        'max_disciplines': max_disciplines
    }

    for _ in range(iterations):
        solution = construct_solution(missing_disciplines, catalog_current, prerequisites, equivalences_map, schedule_map, k, max_disciplines, rare, reproved, prereq_freq)

        solution = local_search(
            solution,
            missing_disciplines,
            catalog_current,
            prerequisites,
            equivalences_map,
            schedule_map,
            rare,
            max_disciplines,
            reproved,
            prereq_freq
        )

        if catalog_previous:
            scoreS = score(solution, rare, reproved, prereq_freq)
        else:
            scoreS = score(solution, set(), reproved, prereq_freq)

        if len(elite_solutions) < elite_limit:
            elite_solutions.append((solution, scoreS))
        else:
            min_score = min(elite_solutions, key=lambda x: x[1])[1]
            if scoreS > min_score:
                idx = next(i for i, (_, s) in enumerate(elite_solutions) if s == min_score)
                elite_solutions[idx] = (solution, scoreS)

        if scoreS > best_score:
            best_score = scoreS
            best_solution = solution

    # Path Relinking entre pares do conjunto elite
    for i in range(len(elite_solutions)):
        for j in range(i + 1, len(elite_solutions)):
            s1, _ = elite_solutions[i]
            s2, _ = elite_solutions[j]
            pr_sol = path_relinking(s1, s2, score, score_args, reproved, rare)
            pr_score = score(pr_sol, rare, reproved, prereq_freq)

            if pr_score > best_score:
                best_score = pr_score
                best_solution = pr_sol

    # Garante que a solução final respeite o limite máximo
    if len(best_solution) > max_disciplines:
        best_solution = best_solution[:max_disciplines]

    return best_solution, best_score
