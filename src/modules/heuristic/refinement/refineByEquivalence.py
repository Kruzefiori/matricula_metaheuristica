import pprint
def get_equivalent_map(equivalences):
    # Cria um dicionário: disciplina -> set de equivalentes
    eq_map = {}
    for item in equivalences:
        base = item['discipline']
        eq_map[base] = set()
        for eq in item['equivalences']:
            # separa equivalências compostas por '+'
            partes = [x.strip() for x in eq.split('+')]
            eq_map[base].update(partes)
            eq_map[base].add(eq.strip())  # também adiciona o original

        eq_map[base].add(base)  # garante que a própria esteja incluída
    return eq_map

def get_all_equivalents(disciplina, eq_map):
    return eq_map.get(disciplina, {disciplina})

def get_aprovadas_com_equivalentes(data_apr, eq_map):
    aprovadas = set(d['disc'] for semestre in data_apr.values() for d in semestre)
    aprovadas_expandidas = set()
    for d in aprovadas:
        aprovadas_expandidas.update(get_all_equivalents(d, eq_map))
    return aprovadas_expandidas

def pontuar_solucao(solucao, catalogo_dict):
    score = 0
    for d in solucao:
        meta = catalogo_dict.get(d, {})
        score += meta.get('blocks', 0)
        if meta.get('oneByYear'):
            score += 10
    return score

def refinement(solucoes, data_apr, equivalences, catalogo):
    eq_map = get_equivalent_map(equivalences)
    aprovadas = get_aprovadas_com_equivalentes(data_apr, eq_map)

    #pprint.pprint(catalogo)
    # Dicionário disciplina -> info
    catalogo_dict = {d['discipline']: d for d in catalogo}
    print("----------------------------")

    solucoes_filtradas = []
    for solucao in solucoes:
        invalida = False
        for disc in solucao:
            if get_all_equivalents(disc, eq_map) & aprovadas:
                invalida = True
                break
        if not invalida:
            score = pontuar_solucao(solucao, catalogo_dict)
            solucoes_filtradas.append((solucao, score))

    # Ordena por pontuação
    solucoes_ordenadas = sorted(solucoes_filtradas, key=lambda x: x[1], reverse=True)
    return solucoes_ordenadas