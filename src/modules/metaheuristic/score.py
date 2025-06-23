def score(solution, rare_disciplines, reproved, prereq_freq):
    total = 0.0
    base_weight = 1.0
    for idx, disc in enumerate(solution):
        peso = base_weight
        # Peso extra que decresce conforme a posição para dar granularidade
        position_factor = 1 / (idx + 1)

        if isinstance(disc, tuple):
            for d in disc:
                p = base_weight
                if d in rare_disciplines:
                    p += 0.7  # peso fracionário para mais granularidade
                if d in reproved:
                    p += 1.5
                p += prereq_freq.get(d, 0) * 0.3
                p += position_factor * 0.1  # influência da posição
                total += p
        else:
            if disc in rare_disciplines:
                peso += 0.7
            if disc in reproved:
                peso += 1.5
            peso += prereq_freq.get(disc, 0) * 0.3
            peso += position_factor * 0.1
            total += peso

    return total