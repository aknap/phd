#!/usr/bin/python3

import re
import spotlight
import os
import pandas as pd
import src.common_functions as cf
from tqdm import tqdm
from nltk.tokenize import sent_tokenize
from multiprocessing.dummy import Pool as ThreadPool


# This code requires a DBpedia Spotlight Docker instance running with a Hungarian model loaded
# Get it here: https://hub.docker.com/r/dbpedia/dbpedia-spotlight

# Type restrictions are from: http://mappings.dbpedia.org/server/ontology/classes/
allowed_types = {'types': 'Agent,Event,Place'}
ignore_set = set(list(['Harmadik_Birodalom', 'Gibson_Guitar_Corporation', 'I._Mátyás_magyar_király']))

# DBpedia Spotlight produces a lot of irrelevant named entity replaces in the texts. To prevent this, a corpus-specific ignore list is needed. A sample list is provided below.
types = str, str
ignore_external = []
with open('data/common/dbpedia_filter_hu_sample.txt', 'r', encoding='utf-8') as file:
    for line in file:
        elements = tuple(t(e) for t, e in zip(types, line.split()))
        ignore_external.append(elements)


def get_named_ent(filename, text):
    error_list = []
    dbpedia_data = []
    if filename not in folder_set:  # Skip already processed files
        sentences = sent_tokenize(text)
        sentences_ner = []
        for sentence in sentences:
            text = " " + sentence + " "
            try:
                db = spotlight.annotate(address='http://localhost:2222/rest/annotate',
                                        text=text,
                                        confidence=0.5,
                                        support=20,
                                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
                                                 "Accept-Encoding": "*",
                                                 "Connection": "keep-alive"}
                                        # filters=allowed_types
                                        )
                if len(db) > 0:
                    for d in db:
                        # Merge words with underscore(s).
                        uri = str(' '.join(d['URI'].split('/')[-1:])).replace('-', '_')

                        # Remove parts in parentheses.
                        uri = re.sub(r'_\(.*\)', '', uri)

                        # Add DBPedia info to a list for error checking.
                        dbpedia_data.append({'original': d['surfaceForm'], 'new': uri, 'uri': d['URI'], 'support': d['support'],
                                             'types': d['types']})

                        # Replace the original text with the dbPedia entity.
                        if (tuple([d['surfaceForm'], uri]) not in ignore_external) and (uri not in ignore_set):
                            text = text.replace(' ' + d['surfaceForm'] + ' ',  ' ' + uri + ' ')
                else:
                    text = sentence
                sentences_ner.append(text.strip())
            except spotlight.SpotlightException:
                sentences_ner.append(text.strip())
                continue
            except Exception as e:
                error_list.append([e, filename])
                raise
        sentences_ner = ' '.join(sentences_ner)
        with open(os.path.join(out_path, filename), 'w', encoding='utf-8') as outfile:
            outfile.write(sentences_ner.strip())
    return error_list, dbpedia_data


if __name__ == '__main__':

    # Load data
    in_path = 'data/interim/txt_accented_urlextract_nospecial_lemmatized'
    out_path = 'data/interim/txt_accented_urlextract_nospecial_lemmatized_ner'
    if not os.path.exists(out_path):
        os.makedirs(out_path, exist_ok=True)

    data_dict = cf.load_folder_to_dict(path=in_path)

    folder_set = set([f for f in os.listdir(out_path)])

    # Run single-threaded
    for filename, text in tqdm(data_dict.items()):
        get_named_ent(filename, text)

    # Run multithreaded
    THREADS_NUM = 32
    pool = ThreadPool(THREADS_NUM)
    pool.starmap(get_named_ent, data_dict.items())

    # Run this to create a dbpedia_list of the found entities
    dbpedia_list = []
    for filename, text in tqdm(data_dict.items()):
        errors, dbpedia = get_named_ent(filename, text)
        for item in dbpedia:
            dbpedia_list.append(item)

    # Create DataFrame to store DBPedia info
    dbpedia_data = pd.DataFrame(columns=['original', 'new', 'uri', 'support', 'types'])
    dbpedia_data.to_csv('data/interim/meta/dbpedia_data_v01.xlsx', encoding='utf-8')
