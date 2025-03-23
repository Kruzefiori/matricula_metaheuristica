import pdfplumber
import argparse
import json
import tabula
import pandas as pd
from pdfquery import PDFQuery
import pandas as pd
import numpy as np


#extrair cada página e montar um JSON com o conteúdo
def getTablesFromPDF(args):
    with pdfplumber.open("./datasets/" + str(args.dataset_name)) as pdf:
        # Ler a tabela da primeira página
        tabela = tabula.read_pdf("./datasets/" + str(args.dataset_name), pages='all', pandas_options={'header': None})
        
#TODO  - Processar a tabela em grupos de 3, cada linha do pdf do histórico gera 3 linhas na tabela de forma errada
#tem que melhorar a leitura do PDF OU agrupar essas linhas corretamente

#TODO - Salvar o resultado em JSON e limpar os dados NULL ou NAN que tem muitos

#TODO - Outra alternativa pode ser usar outra biblioteca para leitura de PDF, como o PyMuPDF (copilot quem indicou) e extrair a tabela de forma correta
#https://pymupdf.readthedocs.io/en/latest/tutorial/#extracting-text
#https://pymupdf.readthedocs.io/en/latest/tutorial/#extracting-text-into-a-json-object
  

        # devolve apenas as 5 primeiras tabelas (TODO: Essa parte precisa ser melhorada, pois, dependendo do PDF, pode ter mais ou menos tabelas)
        return tabela[:6]

def processTables(tables):
    def clean_table(df, tableNumber):
        # ETAPA 1
        # Limpa e formata a tabela removendo colunas desnecessárias e filtrando apenas os dados essenciais.
        df.replace({np.nan: '', '#': '', '*': ''}, inplace=True)  # Remover NaN, '#' e '*'
        # salvando as etapas em um arquivo txt, como: etapa1-tabela[tabelaNumber].txt
        with open(f"./etapa1/etapa1-tabela{tableNumber}.txt", "w") as outfile:
            outfile.write(str(df))

        # ETAPA 2
        # Verificar as colunas em que todas as células estão vazias, e removê-las
        empty_cols = df.columns[df.apply(lambda col: col.astype(str).str.strip().eq('')).all()]
        df.drop(empty_cols, axis=1, inplace=True)
        # salvando as etapas em um arquivo txt, como: etapa2-tabela[tabelaNumber].txt
        with open(f"./etapa2/etapa2-tabela{tableNumber}.txt", "w") as outfile:
            outfile.write(str(df))

        # ETAPA 3
        # 'Ano/Período', 'Ano/Período Letivo', 'Letivo', 'Componente Curricular', 'Componente', 'Curricular', 'Hora', 'Aula', 'hora aula', 'CH', 'Turma', 'Freq %', 'Freq', '%', 'NotaMín' 'Nota', 'Mín'
        # Obtendo as colunas que contêm uma dessas strings, e removendo-as
        unwanted_cols = df.columns[df.apply(lambda col: col.astype(str).str.contains('Ano/Período|Ano/Período Letivo|Letivo|Componente Curricular|Componente|Curricular|Hora|Aula|hora aula|CH|Turma|Freq %|Freq|%|NotaMín|Nota|Mín', case=False, na=False)).any()]
        df.drop(unwanted_cols, axis=1, inplace=True)
        # salvando as etapas em um arquivo txt, como: etapa3-tabela[tabelaNumber].txt
        with open(f"./etapa3/etapa3-tabela{tableNumber}.txt", "w") as outfile:
            outfile.write(str(df))
        
        # ETAPA 4
        # Renumeração das colunas
        df.columns = range(len(df.columns))
        # salvando as etapas em um arquivo txt, como: etapa4-tabela[tabelaNumber].txt
        with open(f"./etapa4/etapa4-tabela{tableNumber}.txt", "w") as outfile:
            outfile.write(str(df))

        # ETAPA 5
        # Verificar as linhas em que todas as células estão vazias, e removê-las
        empty_rows = df.index[df.apply(lambda row: row.astype(str).str.strip().eq('')).all(axis=1)]
        df.drop(empty_rows, inplace=True)
        # salvando as etapas em um arquivo txt, como: etapa5-tabela[tabelaNumber].txt
        with open(f"./etapa5/etapa5-tabela{tableNumber}.txt", "w") as outfile:
            outfile.write(str(df))

        # ETAPA 6
        # Remover as linhas que contêm: 'Média', 'Situação'
        df = df[~df.astype(str).apply(lambda x: x.str.contains('Média|Situação', case=False, na=False).any(), axis=1)]
        # salvando as etapas em um arquivo txt, como: etapa6-tabela[tabelaNumber].txt
        with open(f"./etapa6/etapa6-tabela{tableNumber}.txt", "w") as outfile:
            outfile.write(str(df))

        # ETAPA 7
        # Renumeração das linhas
        df.reset_index(drop=True, inplace=True)
        # salvando as etapas em um arquivo txt, como: etapa7-tabela[tabelaNumber].txt
        with open(f"./etapa7/etapa7-tabela{tableNumber}.txt", "w") as outfile:
            outfile.write(str(df))
        
        # ETAPA 8
        # Adicionar uma nova linha no início da tabela com os nomes das colunas: 'Disciplina', 'Nota', 'Situação'
        df.columns = ['Disciplina', 'Nota', 'Situação']
        # salvando as etapas em um arquivo txt, como: etapa8-tabela[tabelaNumber].txt
        with open(f"./etapa8/etapa8-tabela{tableNumber}.txt", "w") as outfile:
            outfile.write(str(df))

        # Devolver a tabela limpa
        return df
    
    # Processar todas as tabelas
    all_tables = [clean_table(pd.DataFrame(table), i) for i, table in enumerate(tables)]
    
    # Remover tabelas vazias
    all_tables = [table for table in all_tables if table is not None]
    
    # Concatenar todas as tabelas processadas
    final_df = pd.concat(all_tables, ignore_index=True) if all_tables else pd.DataFrame()

    # converter para JSON
    final_json = final_df.to_json(orient="records", force_ascii=False)

    return final_json


# -------------------------------------------------------------------------------------------------------------------------------------------------------------

#só para não lembrar, essa está funcionando mas não está agrupando as linhas corretamente       
def readPDFJ1SON(args):

    with pdfplumber.open("./datasets/" + str(args.dataset_name)) as pdf:
        data = []
        for page in pdf.pages:
            data.append("".join(page.extract_text()))
        tabela = tabula.read_pdf("./datasets/" + str(args.dataset_name), pages='1')
        with open("sample.json", "w") as outfile:
            for tab in tabela:
                outfile.write(tab.to_json(orient="records"))
        return ''
