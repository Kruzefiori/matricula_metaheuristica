# from IPython.display import display
import pandas as pd

#
def parseCSV(period : str):
    if period == "24.1":
        file = "horarios - 24.1"
    elif period == "horarios - 24.2":
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
