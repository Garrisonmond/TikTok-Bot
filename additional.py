import numpy as np
import os
import datetime


import project_configs


default_folder = project_configs.default_folder
source_folder = project_configs.source_folder
temporary_files_folder = project_configs.temporary_files_folder


def sentence_to_words(sentence, sep=None, save_punctuation=False):
    """
    Splits given sentence on words on given separator symbols

    :param sentence: sentenct to split
    :param sep: separator symbol or symbols (array) (if not provided separate on all symbols except letters and numbers)
    :param save_punctuation: to also save punctuation (symbols that get removed are saved in order)

    :return: words
    """

    words = []
    temp = 0
    punctuation = []
    if sep is None:
        sep = list(np.arange(32, 47 + 1)) + list(np.arange(58, 64 + 1)) + list(np.arange(91, 96 + 1)) + list(
            np.arange(123, 126 + 1))
        sep.append(ord('\n'))
        sep.append(ord('\t'))
    else:
        sep = list(map(ord, list(sep)))

    for i in range(len(sentence)):
        ascii = ord(sentence[i])
        if ascii in sep:
            if temp != i:
                words.append(sentence[temp: i])
                punctuation.append(None)
            punctuation.append(sentence[i])
            temp = i + 1
    words.append(sentence[temp: len(sentence)])
    punctuation.append(None)

    if save_punctuation:
        return words, punctuation
    return words


def remove_from_word(word, remove):
    """
    Removes a word from other word

    :param word: word to remove from
    :param remove: word to remove

    :return: new_word
    """

    if not len(remove):
        return word

    new_word = ''
    temp = 0
    i = 0
    while i < len(word):
        if word[i:i + len(remove)] == remove:
            new_word += word[temp:i]
            i += len(remove)
            temp = i
            continue
        i += 1
    new_word += word[temp:i]
    return new_word


def join_words(stripped_words, punctuation):
    """
    Joins given words with provided punctuation

    :param stripped_words: words to join
    :param punctuation: punctuation (arr from 'remove_from_word' func)

    :return: sentence
    """

    if not len(punctuation):
        return stripped_words[0]
    new_word = ''
    j = 0
    for i in punctuation:
        if i is None:
            new_word += stripped_words[j]
            j += 1
        else:
            new_word += i
    return new_word


def read_name_index():
    """
    Reads 'name_index_file' from project_configs.temporary_files

    :return: name_index
    """

    name_index_file = project_configs.temporary_files['name_index_file']

    f = open(name_index_file, mode='r')

    name_index = list(map(int, f.read().split()))[0]

    f.close()

    return name_index


def check_files():
    """
    Checks files from project_configs.temporary_files and creates them if not found

    If 'reddit_login.txt' is not found returns 1

    If 'tiktok_login.txt' is not found returns 2

    If 'sudo_password.txt' is not found returns 3

    If 'instagram_login.txt' is not found returns 4
    """

    if not os.path.exists(temporary_files_folder):
        os.makedirs(temporary_files_folder)

    if not os.path.exists(project_configs.temporary_files['reddit_login_file']):
        return 1

    if not os.path.exists(project_configs.temporary_files['tiktok_login_file']):
        return 2

    if not os.path.exists(project_configs.temporary_files['sudo_password_file']):
        return 3

    if not os.path.exists(project_configs.temporary_files['instagram_login_file']):
        return 3

    if not os.path.exists(project_configs.temporary_files['name_index_file']):
        f = open(project_configs.temporary_files['name_index_file'], mode='w')
        f.write('0')
        f.close()

    if not os.path.exists(project_configs.temporary_files['temp_file']):
        j = i = make_null_dict([project_configs.platforms, project_configs.languages])
        count = make_null_dict([project_configs.platforms, project_configs.languages, project_configs.links])
        write_temp(i, j, count)

    for temp_file in project_configs.temporary_files:
        if not os.path.exists(project_configs.temporary_files[temp_file]):
            f = open(project_configs.temporary_files[temp_file], mode='w')
            f.close()

    for language in project_configs.languages:
        dir = f'{default_folder}{language}'

        if not os.path.exists(dir):
            os.makedirs(dir)

        if not os.path.exists(f'{dir}/videos'):
            os.makedirs(f'{dir}/videos')

    print('File check complete. No critical issues found')


def write_date(upload_date_time=None):
    """
    Writes date in file

    :param upload_date_time: a dictionary of dates to write (if not given write current dates)

    :return:
    """

    date_file = project_configs.temporary_files['date_file']

    f = open(date_file, mode='w')

    today = datetime.date.today()

    for platform in project_configs.platforms:
        for language in project_configs.languages:
            start = datetime.datetime(today.year, today.month, today.day, 0, 0, 0) + datetime.timedelta(days=1)

            if upload_date_time is not None:
                start = upload_date_time[platform][language]

            f.write(f"{start.year}\t{start.month}\t{start.day}\t{start.hour}\t{start.minute}\t{start.second}\n")

    f.close()


def write_name_index(name_index):
    """
    Write name_index into a file

    :param name_index: name_index to write

    :return:
    """

    name_index_file = project_configs.temporary_files['name_index_file']

    f = open(name_index_file, mode='w')

    f.write(str(name_index))

    f.close()


def write_names(names, indexes, links, mode='a'):
    """
    Writes name, j, link into a file

    :param names: names array
    :param mode: if provided describes how to write names

    :return:
    """

    names_file = project_configs.temporary_files['names_file']

    f = open(names_file, mode=mode)

    for i in range(len(names)):
        f.write(f'{names[i]}\t{indexes[i]}\t{links[i]}\n')

    f.close()


def write_shift(shift):
    """
    Writes shift into project_configs.temporary_files['shift_file']
    :param shift: given shift

    :return:
    """

    shift_file = project_configs.temporary_files['shift_file']

    f = open(shift_file, mode='w')

    for platform in project_configs.platforms:
        for language in project_configs.languages:
            f.write(f'{shift[platform][language]}\t')

    f.close()


def write_temp(i_now, j_now, count):
    """
    Writes temp file into project_configs.temporary_files['temp_file']

    :param i_now: given i
    :param j_now: given j
    :param count: given count

    :return:
    """

    temp_file = project_configs.temporary_files['temp_file']

    f = open(temp_file, mode='w')

    for platform in project_configs.platforms:
        for language in project_configs.languages:
            f.write(f'{i_now[platform][language]}\t')
    f.write('\n')

    for platform in project_configs.platforms:
        for language in project_configs.languages:
            f.write(f'{j_now[platform][language]}\t')
    f.write('\n')

    for platform in project_configs.platforms:
        for language in project_configs.languages:
            for link in project_configs.links:
                f.write(f'{count[platform][language][link]}\t')
    f.write('\n')

    f.close()


def read_date():
    """
    Reads dates from project_configs.temporary_files['date_file']

    :return:
    """

    date_file = project_configs.temporary_files['date_file']

    j = open(date_file, mode='r')

    counter = 0
    start = make_null_dict([project_configs.platforms, project_configs.languages])

    lines = list(j.read().split('\n'))

    for platform in project_configs.platforms:
        for language in project_configs.languages:
            year, month, day, hour, minute, second = tuple(map(int, lines[counter].split('\t')))
            temp = datetime.datetime(year, month, day, hour, second)

            start[platform][language] = temp
            counter += 1

    return start


def read_names():
    """
    Reads names from project_configs.temporary_files['names_file']

    :return: names, indexes, links
    """

    names_file = project_configs.temporary_files['names_file']

    f = open(names_file, mode='r')

    lines = list(f.read().split('\n'))

    names = []
    indexes = []
    links = []

    for i in lines[:-1]:
        temp = list(i.split('\t'))
        names.append(temp[0])
        indexes.append(int(temp[1]))
        links.append(temp[2])

    return names, indexes, links


def read_temp():
    """
    Reads temp file from project_configs.temporary_files['temp_file']

    :return: count, i_prev, j_prev
    """

    temp_file = project_configs.temporary_files['temp_file']

    f = open(temp_file, mode='r')

    lines = list(f.read().split('\n'))

    i = list(map(int, lines[0].split('\t')[:-1]))
    j = list(map(int, lines[1].split('\t')[:-1]))
    counters = list(map(int, lines[2].split('\t')[:-1]))

    index1 = 0
    index2 = 0

    count = make_null_dict([project_configs.platforms, project_configs.languages, project_configs.links])
    i_prev = make_null_dict([project_configs.platforms, project_configs.languages])
    j_prev = make_null_dict([project_configs.platforms, project_configs.languages])

    for platform in project_configs.platforms:
        for language in project_configs.languages:
            for link in project_configs.links:
                if index1 >= len(counters):
                    count[platform][language][link] = 0
                else:
                    count[platform][language][link] = counters[index1]
                    index1 += 1

            if index2 >= len(i):
                i_prev[platform][language] = 0
                j_prev[platform][language] = 0
            else:
                i_prev[platform][language] = i[index2]
                j_prev[platform][language] = j[index2]
                index2 += 1

    return count, i_prev, j_prev


def read_shift():
    """
    Reads shift from project_configs.temporary_files['shift_file']

    :return: shift
    """

    shift_file = project_configs.temporary_files['shift_file']

    f = open(shift_file, mode='r')

    temp = list(map(float, f.read().split('\t')[:-1]))

    shift = make_null_dict([project_configs.platforms, project_configs.languages])
    index = 0

    for platform in project_configs.platforms:
        for language in project_configs.languages:
            shift[platform][language] = temp[index]
            index += 1

    return shift


def read_login(platrofm):
    """
    Reads TikTok login information

    :return: login
    """

    login_file = project_configs.temporary_files[f'{platrofm}_login_file']

    f = open(login_file, mode='r')

    lines = list(f.read().split('\t')[:-1])
    login = dict()

    index = 0

    for language in project_configs.languages:
        login[language] = dict()

        login[language]['login'] = lines[index]
        index += 1
        login[language]['password'] = lines[index]
        index += 1

    return login


def make_null_dict(list_of_iter):
    """
    Creates null dictionary based on given list of iterators {list[1]: {list[2]:{...}}}. Elements of iterators are used as keys.

    :param list: given list of iterators

    :return:
    """

    list_of_iter.append(1)

    def make_dict(list_of_iter, index):
        it = list_of_iter[index]

        if it == 1:
            return 0

        temp = dict()

        for i in it:
            temp[i] = make_dict(list_of_iter, index + 1)

        return temp

    return make_dict(list_of_iter, 0)


def read_sudo_password():
    """
    Reads SUDO password form project_configs.temporary_files['sudo_password_file']

    :return:
    """

    sudo_password_file = project_configs.temporary_files['sudo_password_file']

    f = open(sudo_password_file, mode='r')

    return f.read()


def execute_sudo_command(command):
    """
    Executes SUDO command

    :param command: given command to execute

    :return:
    """

    sudo_password = read_sudo_password()
    os.system('echo %s|sudo -S %s' % (sudo_password, command))
