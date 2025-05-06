import random
from typing import List, Dict, Set


def calculate_max_disciplines(student_data: Dict) -> int:
    """Calcula o número máximo de disciplinas baseado no histórico do aluno"""
    total_semesters = len(student_data['aprBySemester'])
    total_disc = sum(len(semester) for semester in student_data['aprBySemester'].values())
    avg_disc_per_semester = total_disc / total_semesters if total_semesters > 0 else 4  # default
    
    pct_apr = student_data['generalStatistics']['scoreAvg'] / 100
    
    return max(1, int(round(avg_disc_per_semester * pct_apr)))


def meets_prerequisites(disc: str, prerequisites: Dict, completed_disc: Set[str]) -> bool:
    """Verifica se o aluno cumpriu todos os pré-requisitos"""
    prereqs = prerequisites.get(disc, {}).get('prerequisites', [])
    return all(prereq in completed_disc for prereq in prereqs)

def calculate_disc_score(disc: str, prerequisites: Dict, available_disc: Dict, neighbor_disc: Dict) -> float:
    """Calcula o score para uma disciplina individual"""
    disc_info = prerequisites.get(disc, {})
    
    # Tipo da disciplina
    disc_type = 1.0 if disc_info.get('isMandatory', False) else 0.5
    
    # Duração da disciplina (anual se oferecida em ambos semestres)
    is_annual = disc in available_disc['uniqueDisciplines'] and disc in neighbor_disc['uniqueDisciplines']
    duration = 1.0 if is_annual else 0.5
    
    # Dependências (disciplinas que esta destrava)
    blocking = 0
    for other_disc, other_info in prerequisites.items():
        if disc in other_info.get('prerequisites', []):
            blocking += 0.2
    
    # Período ideal (simplificação - assumindo que todas são compatíveis)
    period = 0.5
    
    return disc_type + duration - blocking + period


def has_schedule_conflict(current_solution: List[str], new_disc: str, schedule_map: Dict) -> bool:
    """Verifica se a nova disciplina tem conflito com as já selecionadas"""
    for day, times in schedule_map.items():
        for time, discs in times.items():
            if new_disc in discs:
                # Verifica se alguma disciplina na solução está no mesmo horário
                for disc in current_solution:
                    if disc in discs:
                        return True
    return False

def local_search(
    initial_solution: List[str],
    initial_score: float,
    student_data: Dict,
    available_disc: Dict,
    neighbor_disc: Dict,
    prerequisites: Dict,
    max_iterations: int = 1000,
    max_no_improve: int = 50
) -> tuple:
    """Heurística de refinamento por busca local"""
    # Pré-processamento dos dados
    max_disc = calculate_max_disciplines(student_data)
    
    # Disciplinas já cursadas e aprovadas
    completed_disc = set()
    for semester in student_data['aprBySemester'].values():
        completed_disc.update(d['disc'] for d in semester)
    
    # Mapeamento de horários
    schedule_map = {}
    for day, times in available_disc['disciplinesByDayAndTime'].items():
        schedule_map[day] = {}
        for time, discs in times.items():
            schedule_map[day][time] = set(discs)
    
    current_solution = initial_solution.copy()
    current_score = initial_score
    best_solution = current_solution.copy()
    best_score = current_score
    
    no_improve = 0
    iterations = 0
    
    # Disciplinas candidatas (que atendem aos pré-requisitos e não estão na solução)
    candidate_disc = [
        disc for disc in available_disc['uniqueDisciplines'] 
        if meets_prerequisites(disc, prerequisites, completed_disc) and 
        disc not in completed_disc and 
        disc not in current_solution
    ]
    
    while iterations < max_iterations and no_improve < max_no_improve:
        iterations += 1
        
        # Gera vizinho: tenta substituir uma disciplina por outra melhor
        neighbor = current_solution.copy()
        
        # Escolhe aleatoriamente se vai adicionar, remover ou substituir
        move_type = random.choice(['add', 'remove', 'replace'])
        
        improved = False
        
        if move_type == 'add' and len(neighbor) < max_disc:
            # Tenta adicionar uma disciplina que não cause conflito
            random.shuffle(candidate_disc)
            for disc in candidate_disc:
                if not has_schedule_conflict(neighbor, disc, schedule_map):
                    neighbor.append(disc)
                    new_score = sum(
                        calculate_disc_score(d, prerequisites, available_disc, neighbor_disc) 
                        for d in neighbor
                    )
                    if new_score > current_score:
                        current_solution = neighbor
                        current_score = new_score
                        improved = True
                        break
        
        elif move_type == 'remove' and len(neighbor) > 1:
            # Remove a disciplina com menor score
            disc_scores = [
                (disc, calculate_disc_score(disc, prerequisites, available_disc, neighbor_disc)) 
                for disc in neighbor
            ]
            disc_scores.sort(key=lambda x: x[1])
            neighbor.remove(disc_scores[0][0])
            new_score = sum(
                calculate_disc_score(d, prerequisites, available_disc, neighbor_disc) 
                for d in neighbor
            )
            if new_score > current_score:
                current_solution = neighbor
                current_score = new_score
                improved = True
        
        elif move_type == 'replace':
            # Substitui uma disciplina por outra com score potencialmente maior
            if len(neighbor) > 0 and len(candidate_disc) > 0:
                # Encontra a disciplina com menor score na solução
                disc_scores = [
                    (disc, calculate_disc_score(disc, prerequisites, available_disc, neighbor_disc)) 
                    for disc in neighbor
                ]
                disc_scores.sort(key=lambda x: x[1])
                worst_disc, worst_score = disc_scores[0]
                
                # Tenta encontrar uma substituta melhor
                random.shuffle(candidate_disc)
                for new_disc in candidate_disc:
                    new_score = calculate_disc_score(new_disc, prerequisites, available_disc, neighbor_disc)
                    if new_score > worst_score:
                        # Remove a pior e tenta adicionar a nova
                        temp_solution = [d for d in neighbor if d != worst_disc]
                        if not has_schedule_conflict(temp_solution, new_disc, schedule_map):
                            temp_solution.append(new_disc)
                            total_score = sum(
                                calculate_disc_score(d, prerequisites, available_disc, neighbor_disc) 
                                for d in temp_solution
                            )
                            if total_score > current_score:
                                current_solution = temp_solution
                                current_score = total_score
                                improved = True
                                break
        
        if improved:
            no_improve = 0
            if current_score > best_score:
                best_solution = current_solution.copy()
                best_score = current_score
        else:
            no_improve += 1
    
    return best_solution, best_score
