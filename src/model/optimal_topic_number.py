#!/usr/bin/python3

import os
import gensim
import itertools
import gensim.corpora as corpora
import pyLDAvis
import pyLDAvis.gensim_models as gensimvis
import pandas as pd
import xlsxwriter  # Do not remove, required
import openpyxl  # Do not remove, required
from tqdm import tqdm
from gensim.models import CoherenceModel
from multiprocessing import freeze_support
from datetime import datetime
from collections import defaultdict


# NOTICE: This script is written for Gensim version 4+ and uses the LDA Multicore implementation

# This code is used to run models for a range of topic numbers, several times for every topic number.
# The outputs are the models, visualizations, and document-topic Excel files for every run.


def get_document_topic_df(ldamodel, corp, orig_texts, processed_texts):
    # Check if the two datasets are of equal length
    if len(orig_texts) != len(corp):
        raise ValueError('Corpus and original texts length is not equal')
    document_topic_dict = defaultdict(dict)

    # Get main topic in each document
    for i, row in tqdm(enumerate(ldamodel[corp]), desc='Getting dominant topics', total=len(orig_texts)):
        row = sorted(row, key=lambda x: (x[1]), reverse=True)
        # Get dominant topic, percent contribution and keywords for each document
        for j, (topic_num, prop_topic) in enumerate(row):
            if j == 0:  # => dominant topic
                wp = ldamodel.show_topic(topic_num)
                topic_keywords = ', '.join([word for word, prop in wp])
                document_topic_dict[i] = {
                    'dominant_topic': int(topic_num),
                    'percent_contribution': round(prop_topic, 4),
                    'keywords': topic_keywords,
                    'preprocessed_text': processed_texts[i]
                }
            else:
                break

    # Add original documents
    for i, row_data in tqdm(orig_texts.items(), desc='Adding original texts'):
        document_topic_dict[i]['filename'] = row_data['filename']
        document_topic_dict[i]['text'] = row_data['text']

    # Convert to DataFrame
    document_topic_df = pd.DataFrame.from_dict(document_topic_dict, orient='index')
    return document_topic_df


def compute_coherence_values(corpus_dict, corp, texts, limit, start=2, step=1, coherence_metrics=None):
    """
    Compute c_v coherence for various number of topics

    Parameters:
    ----------
    corpus_dict : Gensim dictionary
    corp : Gensim corpus
    texts : List of input texts
    limit : Max num of topics

    Returns:
    -------
    models : List of LDA topic models
    coherence_dict : Coherence values corresponding to the LDA model with respective number of topics
    """
    if coherence_metrics is None:
        coherence_metrics = metrics_to_use
    coherence_dict = defaultdict(dict)
    models = []
    for topic_number in tqdm(range(start, limit, step), desc='Topic number', leave=False):
        model = gensim.models.LdaMulticore(corpus=corp, num_topics=topic_number, workers=number_of_cores_model, id2word=corpus_dict)
        models.append(model)
        for current_metric in coherence_metrics:
            coherence_model = CoherenceModel(model=model, texts=texts, dictionary=corpus_dict, processes=number_of_cores_coherence, coherence=current_metric)
            coherence_value = coherence_model.get_coherence()
            coherence_dict[current_metric][topic_number] = coherence_value
            print('Current model coherence is ' + str(coherence_value) + ' with ' + str(topic_number) + ' topics, using the ' + current_metric + ' metric')
            # Save current coherence value.
            with open(os.path.join(outfile_path, 'coherence_' + current_metric + '_t' + str("{:03d}".format(topic_number)) + '_r' + str(
                    "{:03d}".format(run_number + 1)) + '.coh-' + current_metric),
                      mode='w', encoding='utf-8') as metric_file:
                metric_file.write(str(coherence_value) + '\n')

        # Save model.
        model.save(os.path.join(outfile_path, 'model_topics_t' + str("{:03d}".format(topic_number)) + '_r' + str("{:03d}".format(run_number + 1)) + '.model'), ignore=())

        # Save visualization.
        if save_visualization:
            vis = gensimvis.prepare(model, corp, corpus_dict, sort_topics=False)
            pyLDAvis.save_html(vis, os.path.join(outfile_path, 'visualization_t' + str("{:03d}".format(topic_number)) + '_r' + str("{:03d}".format(run_number + 1)) + '.html'))

        # Save document to topic Excel.
        if save_document_to_topic:
            df_topic_sents_keywords = get_document_topic_df(ldamodel=model, corp=corp, orig_texts=original_documents, processed_texts=txt)
            df_dominant_topic = df_topic_sents_keywords.reset_index()
            df_dominant_topic.columns = ['document_no', 'dominant_topic', 'topic_percent_contribution', 'keywords', 'preprocessed_text', 'filename', 'original_document']
            df_dominant_topic.sort_values(['dominant_topic', 'topic_percent_contribution'], ascending=[True, False], inplace=True)
            df_dominant_topic.reset_index(drop=True, inplace=True)
            excel_writer = pd.ExcelWriter(os.path.join(outfile_path, 'document_dominant_topics_t' + str("{:03d}".format(topic_number)) + '_r' +
                                                       str("{:03d}".format(run_number + 1)) + '.xlsx'), engine='xlsxwriter')
            df_dominant_topic.to_excel(excel_writer)
            excel_writer.close()

    return models, coherence_dict


if __name__ == '__main__':

    # SETTINGS BELOW
    # Number of cores to use for the calculations
    number_of_cores_model = 8
    number_of_cores_coherence = 8

    all_coherence_metrics = ['u_mass', 'c_v', 'c_uci', 'c_npmi']
    metrics_to_use = ['c_v']  # Coherence measures to be used

    coherence_version = 'r01'  # Coherence model directory for version control
    save_document_to_topic = True  # Save document to topic Excel files for each run?
    save_visualization = True  # Save visualization files for each run?

    # Define paths and files
    original_data_file = 'data/raw.csv'
    preprocessed_data_file = 'data/processed.csv'
    outfile_path = f'model/{coherence_version}'
    minimal_length = 5  # Minimal article length (words)

    # Topic ranges
    c_times = 10  # number of times to be run
    c_start = 5  # starting topic number
    c_limit = 21  # max. topic number
    c_step = 1  # stepping interval


    freeze_support()

    start_time = datetime.now()

    # Save settings to a readme file
    with open(os.path.join(outfile_path, 'model_settings.txt'), mode='w', encoding='utf-8') as settings_file:
        settings_file.write(f'''
    # Corpus and output folders
    Preprocessed data file: {preprocessed_data_file}
    Raw corpus folder: {original_data_file}
    Destination folder: {outfile_path}

    # LDA Mallet Model settings
    save document to topic: {save_document_to_topic}
    save visualization: {save_visualization}
    minimal length in words: {minimal_length}
    number of times to run (c_times): {c_times}
    starting topic number (c_start): {c_start}
    maximal topic number (c_limit): {c_limit}
    stepping interval (c_step): {c_step}
    ''')

    # Add all files to a list
    preprocessed_data = pd.read_csv(preprocessed_data_file, sep=';', encoding='utf-8', index_col=0, low_memory=False).squeeze()
    txt_all = list(preprocessed_data)
    txt = [text for text in txt_all if len(text.split(' ')) >= minimal_length]
    print('Corpus loaded')

    # Create lists containing the texts and the words
    txts = []
    for t in txt:
        txts.append(t.strip().split())
    words = list(itertools.chain(*txts))

    # Create dictionary
    dictionary = corpora.Dictionary(txts)

    # Create corpus
    corpus = [dictionary.doc2bow(text) for text in txts]

    # Load original documents
    original_dict = pd.read_csv(original_data_file, sep=';', encoding='utf-8', index_col=0, low_memory=False).squeeze().to_dict()
    original_documents = {}
    c = 0
    for filename, text in original_dict.items():
        original_documents[c] = {'filename': filename, 'text': text}
        c += 1
    print('Original documents loaded')

    # Check for errors
    print('txts length:                 '+str(len(txts)))
    print('corpus length:               '+str(len(corpus)))
    print('original_documents length:   '+str(len(original_documents)))
    if not(len(txts) == len(corpus) == len(original_documents)):
        raise ValueError('Input data lengths do not match')
    else:
        print('Input data lengths match')

    # Run models
    all_coherence_values = defaultdict(dict)
    for run_number in tqdm(range(0, c_times), desc='Run number'):
        model_list, coherence_values = compute_coherence_values(corpus_dict=dictionary, corp=corpus, texts=txts, start=c_start, limit=c_limit, step=c_step)
        all_coherence_values[run_number] = coherence_values

    # Restructure dictionary
    all_coherence_values_new = defaultdict(dict)
    for run_number, values in all_coherence_values.items():
        for metric, runs in values.items():
            all_coherence_values_new[metric][run_number+1] = runs  # +1 to make it intact with the file names

    # Save coherence values to different sheets of the same Excel file
    with pd.ExcelWriter(os.path.join(outfile_path, 'coherence_values.xlsx'), engine='xlsxwriter') as writer:
        for metric, values in all_coherence_values_new.items():
            pd.DataFrame.from_dict(all_coherence_values_new[metric], orient='index').to_excel(writer, sheet_name=metric)
    writer.close()

    end_time = datetime.now()
    print('All finished.\nDuration: {}'.format(end_time - start_time))
