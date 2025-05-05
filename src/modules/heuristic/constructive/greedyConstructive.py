import json
from collections import defaultdict
from modules.heuristic.helpers import helper


def createGreedySolution(availableDisciplines, structuredPdfData , neighborDisciplines):
    helper.organizeData(availableDisciplines, neighborDisciplines)

    