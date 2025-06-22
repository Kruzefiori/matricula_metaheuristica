# from IPython.display import display
import pandas as pd

#
def parseCSVavailableDisciplines(period : str):
    if period == "24.1":
        file = "horarios - 24.1"
    elif period == "24.2":
        file = "horarios - 24.2"
    elif period == "25.1":
        file = "horarios - 25.1"
    path = "./datasets/" + file + '.csv'
    try:
        df = pd.read_csv(path, index_col=0 )

        results = {}
        df_reset = df.reset_index()
        days = df.columns

        for day in days:
            results[day] = {}
            for time_slot in df_reset['Horário'].unique():
                values = df_reset[df_reset['Horário'] == time_slot][day]
                
                disciplines = values.dropna().unique().tolist()

                if disciplines:
                    results[day][time_slot] = disciplines

        distinct_disciplines = set()

        for day, horarios in results.items():
            for time_slot, disciplines in horarios.items():
                distinct_disciplines.update(disciplines)

        lista_disciplinas = sorted(distinct_disciplines)
                    
        return {
            "uniqueDisciplines": lista_disciplinas,
            "disciplinesByDayAndTime": results
        }        
    except FileNotFoundError:
        print(f"File {path} not found.")
        return None
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
    return None

def parseCSVequivalences():
    path = "./datasets/equivalencias.csv"
    try:
        df = pd.read_csv(path)
        # Dicionário intermediário
        equivalencias_dict = {}
        for _, row in df.iterrows():
            discipline = row['CÓDIGO']
            
            equivalentes = []
            for valor in row[1:]:
                if pd.isna(valor) or valor.strip() == "--":
                    continue

                valor = valor.strip()

                # If there is a + they are keep together
                if '+' in valor:
                    equivalentes.append(' + '.join([v.strip() for v in valor.split('+')]))
                else:
                    equivalentes.append(valor)

            if discipline not in equivalencias_dict:
                equivalencias_dict[discipline] = set()

            # Adiciona equivalentes e a própria matéria
            equivalencias_dict[discipline].update(equivalentes)
            #equivalencias_dict[discipline].add(discipline)

        # Converte para lista final
        resultado = [
            {"discipline": materia, "equivalences": sorted(list(eq))}
            for materia, eq in equivalencias_dict.items() 
            if len(eq) > 0
        ]
        return resultado
    except FileNotFoundError:
        print(f"File {path} not found.")
        return None
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
    return None