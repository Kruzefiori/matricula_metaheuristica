def printStructuredData(structuredPdfData):
    # Verifica se os dados estruturados estão vazios
    if not structuredPdfData:
        print("Nenhum dado estruturado encontrado.")
        return

    # Imprime os dados estruturados
    for key, value in structuredPdfData.items():
        print(f"\n{key}: {value}")