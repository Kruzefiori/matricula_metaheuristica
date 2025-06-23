import json
from collections import defaultdict
from modules.heuristic.helpers import helper
import itertools

def createGreedySolution(availableDisciplines, structuredPdfData , neighborDisciplines):
    formatedData = helper.organizeData(availableDisciplines, neighborDisciplines)
    recomendations = getDisciplinesGreedly(structuredPdfData, formatedData)
    return recomendations , formatedData



def canDisciplineBeTaken(disciplines, approveds):
    return all(req in approveds for req in disciplines['requisites'])

def hasConflict(d1, d2):
    for dia in d1['time']:
        if dia in d2['time']:
            h1 = set(d1['time'][dia])
            h2 = set(d2['time'][dia])
            if h1 & h2:
                return True
    return False

def hasConflictInGroup(group):
    for i in range(len(group)):
        for j in range(i + 1, len(group)):
            if hasConflict(group[i], group[j]):
                return True
    return False

def createScore(d):
    score = d.get('blocks', 0)
    if d.get('oneByYear'):
        score += 10
    return score

def getDisciplinesGreedly(data, disciplineCatalog):
    approveds = {d['disc'] for semester in data['aprBySemester'].values() for d in semester}
    missing = set(data['missingDisciplines'])

    # Filtra o catálogo com base nas missing
    candidates = [
        d for d in disciplineCatalog
        if d['discipline'] in missing and canDisciplineBeTaken(d, approveds)
    ]

    # Ordena pela heurística (maior pontuação primeiro)
    candidates.sort(key=createScore, reverse=True)

    resultMatrix = []
    for size in range(len(candidates), 0, -1):
        for grupo in itertools.combinations(candidates, size):
            if not hasConflictInGroup(grupo):
                resultMatrix.append([d['discipline'] for d in grupo])
        if resultMatrix:
            break  # Pega apenas as maiores combinações possíveis sem conflito

    return resultMatrix
    