#!/usr/bin/python3

import pandas as pd
import src.common_functions as cf


if __name__ == '__main__':

    # Load Hungarian sample txts to a dictionary
    hu_12_txt = cf.load_folder_to_dict(path='data/common/sample_hu_12', lower=False, remove_linebreaks=True, minimal_length=0)

    # Convert them to a DataFrame and save in csv
    hu_12_txt_df = pd.DataFrame.from_dict(hu_12_txt, orient='index')
    hu_12_txt_df.to_csv('data/common/sample_hu_12.csv', encoding='utf-8', sep=';', header=False)

    # Load Hungarian sample csv to a dictionary
    hu_12_csv = pd.read_csv('data/common/sample_hu_12.csv', encoding='utf-8', sep=';', low_memory=False, index_col=0, header=None).to_dict(orient='index')
    hu_12_csv = {k: v[1] for k, v in hu_12_csv.items()}

    # Check if the two dicts are equal
    print(hu_12_txt == hu_12_csv)
