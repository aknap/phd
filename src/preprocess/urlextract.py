#!/usr/bin/python3

import os
from tqdm import tqdm
import src.common_functions as cf
from urlextract import URLExtract


if __name__ == '__main__':

    # Load data
    in_path = 'data/interim/txt_accented'
    out_path = 'data/interim/txt_accented_urlextract'
    if not os.path.exists(out_path):
        os.makedirs(out_path, exist_ok=True)

    data_dict = cf.load_folder_to_dict(path=in_path)

    extractor = URLExtract(extract_email=True)

    # Save results
    check_list = []
    url_errors = []
    for file, text in tqdm(data_dict.items(), desc='Processing'):
        url_list = extractor.find_urls(text)
        check_list.append(url_list)
        for url in url_list:
            text = text.replace(url, '')
        with open(os.path.join(out_path, file), 'w', encoding='utf-8') as outfile:
            outfile.write(text)
