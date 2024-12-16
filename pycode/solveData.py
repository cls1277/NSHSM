# Date: 2023/12/5 17:56
# Author: cls1277
# Email: cls1277@163.com

import readData
import os
import pandas as pd

DATANAME = "la"
DATASTART = 1
DATAFINAL = 40
OBJECTIVE = 'makespan'
PROBLEM = 'JSP'

POPSIZE = 100
ITERTHRE = 20000
COUNT = 20
EXPERIMENT = "LocalSearch"
NSs = ['N4', 'N5', 'N6', 'N7', 'N8', 'RAND']
data = pd.DataFrame()
current_path = os.path.dirname(os.path.abspath(__file__))

for i in range(DATASTART, DATAFINAL + 1):
    if i < 10:
        DATASET = DATANAME + "0" + str(i)
    else:
        DATASET = DATANAME + str(i)
    for NS in NSs:
        other_info = 'POPSIZE'+str(POPSIZE)+'_ITERTHRE'+str(ITERTHRE)+'_'+DATASET+'_'+NS
        exper_path = os.path.join(current_path, 'result', EXPERIMENT, other_info)
        # print(exper_path)

        files_data = {}
        for j in range(1, COUNT+1):
            file_name = f'res_{j}.txt'
            result_path =  os.path.join(exper_path, file_name)
            # print(result_path)
            with open(result_path, 'r') as file:
                content = file.read().strip()
                files_data[file_name] = float(content)
        data[NS] = pd.Series(files_data)

    excel_path = os.path.join(current_path, 'excel', EXPERIMENT)
    if not os.path.exists(excel_path):
        os.makedirs(excel_path)
    output_path = os.path.join(excel_path, DATASET+'_output.xlsx')
    data.to_excel(output_path, index=False)

    setting = readData.get_setting(PROBLEM, DATASET)
    data_transformed = (data - setting['optimum']) / setting['optimum']

    data_transformed.loc['Mean'] = data_transformed.mean()
    data_transformed.loc['Std'] = data_transformed.std()

    trans_path = os.path.join(excel_path, DATASET+'_trans.xlsx')
    data_transformed.to_excel(trans_path, index=False)

print("done!")