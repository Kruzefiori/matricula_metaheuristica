from modules.Grasp import greedyRandom

def graspManager(structuredPdfData):
    greedyRandom.pickBestDisciplineRandomly(structuredPdfData.get("missingDisciplines", []))
    pass