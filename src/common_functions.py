import tqdm
import os


def load_folder_to_dict(path=None, lower=False, remove_linebreaks=True, minimal_length=0):
    """
    Load a folder's content to a dictionary (data_dict) where the keys are the filenames, and the values are the file contents
    :param path: Path to the folder to be loaded
    :param lower: Convert text to lowercase
    :param remove_linebreaks: Replace line breaks with spaces
    :param minimal_length: Specify minimal document length in N of words
    :return: Dict of loaded files where the keys are the filenames, and the values are the files' contents
    """
    if path is None:
        raise ValueError('No valid path specified.')
    if minimal_length == 0:
        print('No minimal document length specified - loading all files.')
    else:
        print('Minimal document length is %i words' % minimal_length)
    if lower:
        print('Converting text to lowercase.')
    data_dict = {}
    for file in tqdm.tqdm(os.listdir(path), desc='Loading files to dictionary'):
        with open(os.path.join(path, file), 'r', encoding='utf-8') as infile:
            if remove_linebreaks:
                document = infile.read().strip().replace('\n', ' ')
            else:
                document = infile.read().strip()
            if lower:
                document = document.lower()
            else:
                document = document
        if minimal_length != 0:
            if len(document.split(' ')) > minimal_length:
                data_dict[file] = document
        else:
            data_dict[file] = document
    return data_dict


def save_dict_to_txts(data=None, out_path=None):
    """
    Save a data_dict's content to separate txt files to a specified folder
    :param data: The dictionary containing data to be saved
    :param out_path: Folder where the txt files should be saved
    :return: none.
    """
    if data is None:
        raise ValueError('No valid data source specified.')
    if out_path is None:
        raise ValueError('No valid out path and file specified.')
    for filename, text in tqdm.tqdm(data.items(), desc='Writing files'):
        if not filename.endswith('.txt'):
            filename = f'{filename}.txt'
        with open(os.path.join(out_path, filename), 'w', encoding='utf-8') as outfile:
            outfile.write(text)


def dump_corpus_to_csv(data=None, out_path=None):
    """
    Dump a data_dict's content to a single csv file. The output file contains only the texts, no IDs or dict keys are written
    :param data: The dictionary containing data to be saved
    :param out_path: Folder and files where the csv file should be saved
    :return: none.
    """
    if data is None:
        raise ValueError('No valid data source specified.')
    if out_path is None:
        raise ValueError('No valid out path and file specified.')
    with open(out_path, mode='w', encoding='utf-8') as outfile:
        for filename, text in tqdm.tqdm(data.items(), desc='Writing text file'):
            outfile.writelines(text+'\n')
