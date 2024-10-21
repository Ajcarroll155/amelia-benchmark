import csv
import io
import pandas as pd
from pandas import DataFrame

def process_uprof_csv(upload: str) -> dict:
    with open(upload, 'r') as csvFile:
        reader = csv.reader(csvFile)

        file_context = ""
        file_data = {}
        csv_rows = []
        for row in reader:
            csv_rows.append(row)
        csvFile.close()
    for i in range(0,len(csv_rows)):
        row = csv_rows[i]
        if 'CPU Topology:' in row:
            i = i + 1
            row = csv_rows[i]
            cpu_top_list = []
            while len(row) == 3:
                cpu_top_list.append(row)
                i = i+1
                row = csv_rows[i]
            cpu_top_df = DataFrame(data=cpu_top_list[1:],columns=cpu_top_list[0])
            file_data['cpu_topology'] = cpu_top_df
        elif 'CORE METRICS' in row:
            i = i + 1
            place = i
            row = csv_rows[i]
            while has_blanks(row):
                i = i + 1
                row = csv_rows[i]
            prof_data_list = csv_rows[i:]
            prof_df = create_dataframe(prof_data_list)
            file_data['core_metrics'] = prof_df
        elif len(row) == 0:
            file_context = file_context + '\n'
        elif len(row) == 1:
            file_context = file_context + row[0] + '\n'
        elif len(row) == 2:
            file_context = file_context + f"{row[0]} {row[1]}\n"

    file_data['report'] = file_context
    
    print(f'Report Summary: {file_context}\nCPU Topology:\n{cpu_top_df.head(3)}\nCore Metrics:\n{prof_df.head(3)}')

    return file_data

def create_dataframe(data:list) -> DataFrame:
    while [] in data:
        data.remove([])
    print(data)
    row_headers = False
    try: float(data[1][0])
    except: row_headers = True

    if row_headers:
        cols = data[0][1:]
        indexes = []
        for i in range(1, len(data)):
            indexes.append(data[i][0])

        df_input = {}
        for i in range(0,len(cols)):
            col_name = cols[i]
            col_vals = []
            for j in range(1,len(data)):
                col_vals.append(data[j][i+1])
            col_series = pd.Series(data=col_vals, index=indexes)
            df_input[col_name] = col_series
        
        return DataFrame(df_input, dtype=float)
    else:
        cols = data[0]
        for row in data:
            row.remove('')
        return DataFrame(data[1:], columns=cols, dtype=float)

def has_blanks(row:list) -> bool:
    for elem in row[0:-1]:
        if elem == '':
            return True
    return False