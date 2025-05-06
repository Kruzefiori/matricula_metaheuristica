import random
from time import time as Time
from typing import List, Dict, Set

def calculate_max_disciplines(student_data: Dict) -> int:
    """Calcula o número máximo de disciplinas baseado no histórico do aluno"""
    total_semesters = len(student_data['aprBySemester'])
    total_disc = sum(len(semester) for semester in student_data['aprBySemester'].values())
    avg_disc_per_semester = total_disc / total_semesters if total_semesters > 0 else 4  # default
    
    pct_apr = student_data['generalStatistics']['scoreAvg'] / 100
    
    return max(1, int(round(avg_disc_per_semester * pct_apr)))

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

def random_constructive(
    student_data: Dict,
    available_disc: Dict,
    neighbor_disc: Dict,
    prerequisites: Dict,
    max_attempts: int = 100
) -> tuple:
    """Heurística construtiva aleatória"""
    initTimer = Time()
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
    
    best_solution = []
    best_score = 0
    
    for _ in range(max_attempts):
        current_solution = []
        remaining_disc = [
            disc for disc in available_disc['uniqueDisciplines'] 
            if meets_prerequisites(disc, prerequisites, completed_disc) and 
            disc not in completed_disc
        ]
        random.shuffle(remaining_disc)
        
        for disc in remaining_disc:
            if len(current_solution) >= max_disc:
                break
            
            if not has_schedule_conflict(current_solution, disc, schedule_map):
                current_solution.append(disc)
        
        current_score = sum(
            calculate_disc_score(disc, prerequisites, available_disc, neighbor_disc) 
            for disc in current_solution
        )
        
        if current_score > best_score:
            best_solution = current_solution
            best_score = current_score

    # Finaliza o temporizador
    endTimer = Time()
    elapsed_time = endTimer - initTimer
    
    return best_solution, best_score, elapsed_time
