import requests
import moviepy.editor as me
import numpy as np
import pyttsx3
import datetime
import nltk
import urlextract
import os
from googletrans import Translator

import video_description
import additional
import project_configs

default_folder = project_configs.default_folder
source_folder = project_configs.source_folder
temporary_files_folder = project_configs.temporary_files_folder


def login():
    """
    Logins on Reddit based on values in project_configs.temporary_files['reddit_login_file']

    :return: headers
    """

    reddit_login_file = project_configs.temporary_files['reddit_login_file']

    f = open(reddit_login_file)
    s = f.read().split('\t')
    personal, secret, username, password = s[0], s[1], s[2], s[3]

    auth = requests.auth.HTTPBasicAuth(personal, secret)
    data = {'grant_type': 'password',
            'username': username,
            'password': password}
    headers = {'User-Agent': 'TikTok'}
    res = requests.post('https://www.reddit.com/api/v1/access_token',
                        auth=auth, data=data, headers=headers)
    TOKEN = res.json()['access_token']
    headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

    print('Login complete')

    return headers


def delete_uploaded_videos():
    """
    Deletes already uploaded videos and corrects all needed information

    :return:
    """

    name_index = additional.read_name_index()
    names, indexes, links = additional.read_names()
    count, i_prev, j_prev = additional.read_temp()

    min_i = 0
    flag = 1

    for platform in project_configs.platforms:
        for language in project_configs.languages:
            if flag or i_prev[platform][language] < min_i:
                min_i = i_prev[platform][language]
                flag = 0

    for language in project_configs.languages:
        for i in range(name_index):
            for j in range(indexes[i]):
                video_name = f'{i}_{j}.mpg'
                video = f'{default_folder}{language}/videos/{video_name}'

                if not os.path.exists(video):
                    continue

                if i < min_i:
                    os.remove(video)
                else:
                    new_video_name = f'{i - min_i}_{j}.mpg'
                    new_video = f'{default_folder}{language}/videos/{new_video_name}'
                    os.rename(video, new_video)

    for platform in project_configs.platforms:
        for language in project_configs.languages:
            i_prev[platform][language] = i_prev[platform][language] - min_i

    additional.write_names(names[min_i:], indexes[min_i:], links[min_i:], mode='w')
    additional.write_temp(i_prev, j_prev, count)
    additional.write_name_index(name_index - min_i)

    print("Already uploaded videos are successfully deleted")


def hard_filter(comment, min_len=None, max_len=None, manual=None):
    """
    Wrapper function of all used HARD filters. Skips a comment if requirement of any filter is not met.

    :param comment: text to filter
    :param min_len: minimal length of text (if not provided do not use to filter)
    :param max_len: maximal length of text (if not provided do not use to filter)
    :param manual: if given, enables manual filtration

    :return: result
    """
    result = True
    if result:
        result = filter_len(comment, min_len, max_len)
    if result:
        result = filter_bad_words(comment)
    if result and manual is not None:
        result = manual_filter(comment)

    return result


def filter_len(comment, min_len=None, max_len=None):
    """
    Check length of a given text

    :param comment: text to filter
    :param min_len: minimal length of text (If not provided do not use to filter)
    :param max_len: maximal length of text (if not provided do not use to filter)

    :return: result
    """

    length = len(comment)
    if min_len is None:
        min_len = length
    if max_len is None:
        max_len = length
    if min_len <= length <= max_len:
        return True
    return False


def filter_bad_words(comment):
    """
    Check given text for 'swear' words from project_configs.temporary_files['not_allowed_file']

    :param comment: text to filter

    :return: result
    """

    not_allowed_file = project_configs.temporary_files['not_allowed_file']

    if comment is None:
        return False

    f = open(not_allowed_file, mode='r')
    not_allowed = f.read().split('\t')[:-1]

    words = list(map(lemmatize_word, additional.sentence_to_words(comment, None)))

    for word in words:
        if word in not_allowed:
            return False

    return True


def get_tag(word):
    """
    Returns word tag

    :param word: given word to find tag

    :return: tag
    """

    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {
        'J': nltk.corpus.wordnet.ADJ,
        'N': nltk.corpus.wordnet.NOUN,
        'V': nltk.corpus.wordnet.VERB,
        'R': nltk.corpus.wordnet.ADV
    }

    return tag_dict.get(tag, nltk.corpus.wordnet.NOUN)


def lemmatize_word(word):
    """
    Lemmatizes word using NLTK and pos_tag

    :param word: given word to lemmatize

    :return: lemmatized_word
    """

    wnl = nltk.stem.WordNetLemmatizer()
    word = word.lower()

    return wnl.lemmatize(word, get_tag(word))


def manual_filter(comment):
    """
    Makes a manual filtration of a given text

    :param comment: text to filter

    :return: result
    """

    if comment is None:
        return False

    print(f'{comment}\n')

    while 1:
        print('Use this title?')
        print(f'\n>>> ', end='')
        use = input()
        print()

        if len(use) == 1 and (int(use) == 1 or int(use) == 0):
            break

        print('Unexpected input')

    if not int(use):
        return False

    return True


def filter_text(comment):
    """
    Removes from given text words from project_configs.temporary_files['remove_file']

    :param comment: text to filter

    :return: filtered_text
    """

    remove_file = project_configs.temporary_files['remove_file']

    f = open(remove_file, mode='r')

    words_to_remove = f.read().split('\t')[:-1]

    words = additional.sentence_to_words(comment, ' ')

    for remove in words_to_remove:
        for j in range(len(words)):
            words[j] = additional.remove_from_word(words[j], remove)

            if words[j] == '&':
                words[j] = 'and'

    comment = ' '.join(words)

    return comment


def shear_site(headers, link, nsfw=True):
    """
    Shears Reddit based on given link

    :param headers: Reddit headers file
    :param link: a link from project_configs.links['link']
    :param nsfw: use only NSFW posts

    :return: titles, urls
    """

    titles = []
    urls = []

    res = requests.get(link, headers=headers)

    for topic in res.json()['data']['children']:

        if topic['data']['whitelist_status'] != 'promo_adult_nsfw' and nsfw:
            continue

        title = topic['data']['title']

        if not hard_filter(title):
            continue

        title = filter_text(title)
        titles.append(title)
        urls.append(topic['data']['url'].replace('//www.reddit.com', '//oauth.reddit.com'))

    print(f'{link} has been successfully parsed')

    return titles, urls


def get_com(url, headers, link):
    """
    Wrapper function of getting comments and answers based on given thread url

    :param url: thread url form 'urls' array
    :param headers: Reddit headers file
    :param link: a link from project_configs.links

    :return: comments, answers
    """

    res = requests.get(url, headers=headers)

    comments, answers = globals()[f'get_com_{link}'](res)

    return comments, answers


def get_com_ask(res):
    """
    Parses AskReddit thread comments

    :param res: a result of request

    :return: comments, answers
    """

    comments = []

    for com in res.json()[1]['data']['children'][:-1]:
        if not (int(com['data']['created']) % 2 == 0):
            continue
        comment = com['data']['body']

        if not hard_filter(com['data']['body'], 400, 900):
            continue

        comment = filter_text(comment)
        comments.append(comment)

    return comments, [''] * len(comments)


def get_com_ama(res):
    """
    Parses IAMA thread comments

    :param res: a result of request

    :return: comments, answers
    """

    comments = []
    answers = []

    author = res.json()[0]['data']['children'][0]['data']['author']
    for com in res.json()[1]['data']['children'][:-1]:
        if not ('data' in com['data']['replies'] and (int(com['data']['created']) % 2 == 0)):
            continue
        for ans in com['data']['replies']['data']['children'][:-1]:

            if ans['data']['author'] != author:
                continue

            comment = com['data']['body']
            answer = ans['data']['body']

            if hard_filter(comment, None, 900) and hard_filter(answer, 400, 900):
                answer = filter_text(answer)
                comment = filter_text(comment)
                answers.append(answer)
                comments.append(comment)

            break

    return comments, answers


def translate_comment(comment):
    """
    Translates a given text to all languages from project_configs.languages

    :param comment: text to translate

    :return: translated_comments
    """

    translator = Translator()
    translated_comments = dict()

    if comment == '':
        for language in project_configs.languages:
            translated_comments[language] = ''
    else:
        for language in project_configs.languages:
            translated_comments[language] = translator.translate(comment, dest=language, src="en").text

    return translated_comments


def filter_audio(comment):
    """
    Filters a given text to further voicing (removes links, nsfw words and expands abbreviations)

    :param comment: text to filter

    :return: filtered_text
    """

    words = additional.sentence_to_words(comment, ' ')

    extractor = urlextract.URLExtract()
    extractor.extract_email = True
    for j in range(len(words)):
        links = extractor.find_urls(words[j])
        for link in links:
            words[j] = additional.remove_from_word(words[j], link)
        stripped_words, punctuation = additional.sentence_to_words(words[j], save_punctuation=True)

        stripped_words = check_nsfw(stripped_words)
        stripped_words = expand_abbreviation(stripped_words)

        words[j] = additional.join_words(stripped_words, punctuation)
    comment = ' '.join(words)
    return comment


def check_nsfw(stripped_words):
    """
    Check if a given word in a given list in nsfw list from project_configs.temporary_files['nsfw_words_file']

    :param stripped_words: given list of words

    :return: checked_word
    """

    nsfw_words_file = project_configs.temporary_files['nsfw_words_file']

    f = open(nsfw_words_file, mode='r')

    nsfw_words = f.read().split('\n')[:-1]

    for i in range(len(stripped_words)):
        stripped_word = stripped_words[i].lower()

        if lemmatize_word(stripped_word) in nsfw_words:
            stripped_words[i] = ''

    return stripped_words


def expand_abbreviation(stripped_words):
    """
    Expands given list of abbreviations

    :param stripped_words: given list of abbreviations

    :return: expanded_abbreviation
    """

    for i in range(len(stripped_words)):
        stripped_word = stripped_words[i].lower()

        if stripped_word in project_configs.abbreviations:
            stripped_words[i] = project_configs.abbreviations[stripped_word][:1].upper() + \
                                project_configs.abbreviations[stripped_word][1:]
            continue

        stripped_words[i] = stripped_word[:1].upper() + stripped_word[1:]

    return stripped_words


def voice(comments, tag):
    """
    Voices a given translated texts to all languages from project_configs.languages and saves them

    :param comments: dictionary of traslated texts
    :param tag: tag of text

    :return:
    """

    for language in project_configs.languages:
        save_path = f'{default_folder}{language}/{tag}.mp3'
        tts = configure_voice(language)
        tts.save_to_file(filter_audio(comments[language]), save_path)
        tts.runAndWait()
        tts = 0


def configure_voice(language):
    """
    Configures tts based on given languages and params from project_configs.languages[language]['voice']

    :param language: a given language

    :return: tts
    """

    voice_names = project_configs.languages[language]['voice']['name']
    rate = project_configs.languages[language]['voice']['rate']
    num = int(np.random.randint(0, len(voice_names), size=1))
    tts = pyttsx3.init()
    voices = tts.getProperty('voices')

    for voice in voices:
        if voice.name == voice_names[num]:
            tts.setProperty('voice', voice.id)
            break
    tts.setProperty('rate', rate[num])

    return tts


def make_video(title, comment, answer, link, language, name_index, j):
    """
    Function that makes and saves a video

    :param title: given title
    :param comment: given comment
    :param answer: given answer
    :param link: given link from project_configs.links
    :param language: language from project_configs.languages
    :param name_index: given name_index
    :param j: index of a given comment

    :return:
    """

    video_name = f'{name_index}_{j}.mpg'
    video = f'{default_folder}{language}/videos/{video_name}'

    txt_params = project_configs.txt_params
    pause_time = project_configs.pause_time

    audio, duration_title, duration_comment, duration_answer = globals()[f'make_audio_{link}'](pause_time, language)
    duration = duration_comment + duration_title + duration_answer
    background_size, background_path = make_background(duration, language)
    txt_path = globals()[f'make_txt_{link}'](title, comment, answer, duration_title, duration_comment, duration_answer,
                                             txt_params, background_size, audio, language)

    os.system(
        f'ffmpeg -i {background_path} -i {txt_path} -filter_complex "overlay={background_size[0] * 0.05}:'
        f'{background_size[1] * 0.2}" -map "1:a:0" -max_muxing_queue_size 9999  {video} -y')


def make_audio_ask(pause_time, language):
    """
    Makes an ask audio clip

    :param pause_time: pause time from project_configs.pause_time
    :param language: a given language

    :return: audio, duration_title, duration_comment, duration_answer
    """

    title_mp3_file = f'{default_folder}{language}/title.mp3'
    comment_mp3_file = f'{default_folder}{language}/comment.mp3'

    title_audio = me.AudioFileClip(title_mp3_file)
    title_audio = title_audio.set_duration(title_audio.duration - 0.1)
    comment_audio = me.AudioFileClip(comment_mp3_file)
    comment_audio = comment_audio.set_duration(comment_audio.duration - 0.1)
    pause = title_audio.subclip(0, pause_time).volumex(0)
    audio = me.concatenate_audioclips([title_audio, pause, comment_audio])
    duration_title = title_audio.duration + pause_time
    duration_comment = comment_audio.duration

    return audio, duration_title, duration_comment, 0


def make_audio_ama(pause_time, language):
    """
    Makes an ama audio clip

    :param pause_time: pause time from project_configs.pause_time
    :param language: a given language

    :return: audio, duration_title, duration_comment, duration_answer
    """

    title_mp3_file = f'{default_folder}{language}/title.mp3'
    comment_mp3_file = f'{default_folder}{language}/comment.mp3'
    answer_mp3_file = f'{default_folder}{language}/answer.mp3'

    title_audio = me.AudioFileClip(title_mp3_file)
    title_audio = title_audio.set_duration(title_audio.duration - 0.1)
    comment_audio = me.AudioFileClip(comment_mp3_file)
    comment_audio = comment_audio.set_duration(comment_audio.duration - 0.1)
    answer_audio = me.AudioFileClip(answer_mp3_file)
    answer_audio = answer_audio.set_duration(answer_audio.duration - 0.1)
    pause = title_audio.subclip(0, pause_time).volumex(0)
    audio = me.concatenate_audioclips([title_audio, pause, comment_audio, pause, answer_audio])
    duration_title = title_audio.duration + pause_time
    duration_comment = comment_audio.duration + pause_time
    duration_answer = answer_audio.duration

    return audio, duration_title, duration_comment, duration_answer


def make_background(duration, language):
    """
    Loads and makes a background clip

    :param duration: given duration of a clip
    :param language: given language

    :return: background_size, background_file
    """

    if duration < 59:
        num = int(np.random.randint(0, 3, size=1))
    elif duration < 90:
        num = int(np.random.randint(1, 3, size=1))
    else:
        num = int(np.random.randint(2, 3, size=1))

    backgroud_file = f'{source_folder}src{num}.mp4'
    save_path = f'{default_folder}{language}/temp_background.mp4'

    backgroud = me.VideoFileClip(backgroud_file)
    time = str(datetime.timedelta(seconds=int(duration)))
    os.system(f'ffmpeg -ss 00:00:00 -t {time} -i {backgroud_file} -vcodec copy -acodec copy {save_path} -y')

    return backgroud.size, save_path


def make_txt_ask(title, comment, answer, duration_title, duration_comment,
                 duration_answer, txt_params, size, audio, language):
    """
    Makes an ask txt clip

    :param title: given title
    :param comment: given comment
    :param answer: given answer
    :param duration_title:  given duration of title clip
    :param duration_comment: given duration of comment clip
    :param duration_answer: given duration of answer clip
    :param txt_params: txt params from project_configs.txt_params
    :param size: size of a background clip
    :param audio: given audio clip
    :param language: given language

    :return: txt_clip_file
    """

    txt_clip_file = f'{default_folder}{language}/txt_clip.mp4'

    image = make_image()
    size_multiplier = project_configs.multiplier * size[1]

    txt_title = me.TextClip(
        title,
        font=txt_params['font'],
        size=txt_params['size'],
        fontsize=txt_params['title_fontsize'],
        bg_color=txt_params['bg_color'],
        color=txt_params['color'],
        align=txt_params['align'],
        method=txt_params['method']
    )
    title_w, title_h = txt_title.size
    txt_title = txt_title.set_position((project_configs.offset_w, project_configs.offset_h))
    title_clip = me.CompositeVideoClip([image, txt_title]).set_duration(duration_title)

    txt_comment = me.TextClip(
        comment,
        font=txt_params['font'],
        size=txt_params['size'],
        fontsize=txt_params['comment_fontsize'],
        bg_color=txt_params['bg_color'],
        color=txt_params['color'],
        align=txt_params['align'],
        method=txt_params['method']
    )
    txt_comment = txt_comment.set_position(
        (project_configs.offset_w, project_configs.offset_h + title_h + project_configs.offset_m))
    comment_clip = me.CompositeVideoClip([image, txt_title, txt_comment]).set_duration(duration_comment)
    txt_clip = me.concatenate_videoclips([title_clip, comment_clip])
    txt_clip = txt_clip.resize(width=txt_clip.size[0] * size_multiplier)
    txt_clip = txt_clip.set_position('center')
    txt_clip = txt_clip.set_audio(audio)
    txt_clip.write_videofile(txt_clip_file, fps=1)

    return txt_clip_file


def make_txt_ama(title, comment, answer, duration_title, duration_comment,
                 duration_answer, txt_params, size, audio, language):
    """
   Makes an ama txt clip

   :param title: given title
   :param comment: given comment
   :param answer: given answer
   :param duration_title:  given duration of title clip
   :param duration_comment: given duration of comment clip
   :param duration_answer: given duration of answer clip
   :param txt_params: txt params from project_configs.txt_params
   :param size: size of a background clip
   :param audio: given audio clip
   :param language: given language

   :return: txt_clip_file
   """

    txt_clip_file = f'{default_folder}{language}/txt_clip.mp4'

    size_multiplier = project_configs.multiplier * size[1]
    image = make_image()

    txt_title = me.TextClip(
        title,
        font=txt_params['font'],
        size=txt_params['size'],
        fontsize=txt_params['title_fontsize'],
        bg_color=txt_params['bg_color'],
        color=txt_params['color'],
        align=txt_params['align'],
        method=txt_params['method']
    )
    title_w, title_h = txt_title.size
    txt_title = txt_title.set_position((project_configs.offset_w, project_configs.offset_h))
    title_clip = me.CompositeVideoClip([image, txt_title]).set_duration(duration_title)

    txt_comment = me.TextClip(
        comment,
        font=txt_params['font'],
        size=txt_params['size'],
        fontsize=txt_params['comment_fontsize'],
        bg_color=txt_params['bg_color'],
        color=txt_params['color'],
        align=txt_params['align'],
        method=txt_params['method']
    )
    txt_comment = txt_comment.set_position(
        (project_configs.offset_w, project_configs.offset_h + title_h + project_configs.offset_m))
    comment_clip = me.CompositeVideoClip([image, txt_title, txt_comment]).set_duration(duration_comment)

    txt_answer = me.TextClip(
        answer,
        font=txt_params['font'],
        size=txt_params['size'],
        fontsize=txt_params['comment_fontsize'],
        bg_color=txt_params['bg_color'],
        color=txt_params['color'],
        align=txt_params['align'],
        method=txt_params['method']
    )
    txt_answer = txt_answer.set_position(
        (project_configs.offset_w, project_configs.offset_h + title_h + project_configs.offset_m))
    answer_clip = me.CompositeVideoClip([image, txt_title, txt_answer]).set_duration(duration_answer)
    txt_clip = me.concatenate_videoclips([title_clip, comment_clip, answer_clip])
    txt_clip = txt_clip.resize(width=txt_clip.size[0] * size_multiplier)
    txt_clip = txt_clip.set_position('center')
    txt_clip = txt_clip.set_audio(audio)
    txt_clip.write_videofile(txt_clip_file, fps=1)

    return txt_clip_file


def make_image():
    """
    Loads an image file

    :return: image
    """

    num = int(np.random.randint(3, size=1))
    image_file = f'{source_folder}img{num}.jpg'
    image = me.ImageClip(image_file)

    return image


def add_outro(video_name, language):
    """
    Adds outros to a given video

    :param video_name: given video name
    :param language: given language

    :return:
    """

    video = f'{default_folder}{language}/videos/{video_name}'

    youtube_folder = f'{default_folder}{language}/youtube/'
    tiktok_folder = f'{default_folder}{language}/tiktok/'
    instagram_folder = f'{default_folder}{language}/instagram/'

    youtube_mpg_path = f'{source_folder}youtube.mpg'
    tiktok_mpg_path = f'{source_folder}tiktok.mpg'
    instagram_mpg_path = f'{source_folder}instagram.mpg'

    temp_file = f'{default_folder}{language}/temp.mpg'

    os.system(f'ffmpeg -i {video} -qscale 0 {temp_file} -y')

    output_file = f'{youtube_folder}{video_name}'
    os.system(f'cat {temp_file} {youtube_mpg_path} | ffmpeg -f mpeg -i - -qscale 0 -vcodec mpeg4 {output_file} -y')

    output_file = f'{tiktok_folder}{video_name}'
    os.system(f'cat {temp_file} {tiktok_mpg_path} | ffmpeg -f mpeg -i - -qscale 0 -vcodec mpeg4 {output_file} -y')

    output_file = f'{instagram_folder}{video_name}'
    os.system(f'cat {temp_file} {instagram_mpg_path} | ffmpeg -f mpeg -i - -qscale 0 -vcodec mpeg4 {output_file} -y')


def remove_production_files():
    """
    Removes temporary files used in video-production

    :return:
    """

    for language in project_configs.languages:
        if os.path.exists(f'{default_folder}{language}/answer.mp3'):
            os.remove(f'{default_folder}{language}/answer.mp3')

        if os.path.exists(f'{default_folder}{language}/comment.mp3'):
            os.remove(f'{default_folder}{language}/comment.mp3')

        if os.path.exists(f'{default_folder}{language}/title.mp3'):
            os.remove(f'{default_folder}{language}/title.mp3')

        if os.path.exists(f'{default_folder}{language}/temp_background.mp4'):
            os.remove(f'{default_folder}{language}/temp_background.mp4')

        if os.path.exists(f'{default_folder}{language}/txt_clip.mp4'):
            os.remove(f'{default_folder}{language}/txt_clip.mp4')


def max_len_tags():
    """
    Calculates maximal length of tags

    :return:  max_len
    """

    max_len = 0

    for tag in video_description.tags:
        if len(video_description.tags[tag]) > max_len:
            max_len = len(video_description.tags[tag])

    return max_len


def make_names(titles, flags):
    """
    Makes names for given titles

    :param titles: given titles
    :param flags: given flags (stores link information and amount of videos)

    :return: names
    """

    tags_len = max_len_tags()
    max_len = 90

    names = []
    indexes = []
    links = []

    for link in project_configs.links:
        for i in range(len(titles[link])):

            if not flags[link][i]:
                continue

            print(titles[link][i])
            print('\nInput name in english\n\n>>> ', end='')

            while 1:
                name = input()
                if len(name) + tags_len <= max_len:
                    break
                print(f'\nName is too long ({len(name)}). No more than {max_len - tags_len} symbols.\n\n>>> ', end='')

            print()

            names.append(name)
            indexes.append(flags[link][i])
            links.append(link)

    return names, indexes, links


def main():
    if additional.check_files() == 1:
        print('No Reddit login file found')
        print('Exiting...')
        return

    headers = login()

    TITLES = dict()
    URLS = dict()
    flags = dict()

    delete_uploaded_videos()
    name_index = additional.read_name_index()

    for link in project_configs.links:
        TITLES[link], URLS[link] = shear_site(headers, project_configs.links[link]['link'],
                                              project_configs.links[link]['check_nsfw'])
        flags[link] = [0] * len(TITLES[link])

    for link in project_configs.links:
        for i in range(len(TITLES[link])):
            title = TITLES[link][i]
            url = URLS[link][i]
            comments, answers = get_com(url, headers, link)

            if len(comments) == 0:
                continue

            flags[link][i] = len(comments)

            translated_titles_text = translate_comment(title)
            translated_titles_audio = translate_comment(filter_audio(title))

            voice(translated_titles_audio, 'title')

            for j in range(len(comments)):
                comment = comments[j]
                answer = answers[j]

                translated_comments_text = translate_comment(comment)
                translated_comments_audio = translate_comment(filter_audio(comment))
                translated_answers_text = translate_comment(answer)
                translated_answers_audio = translate_comment(filter_audio(answer))

                voice(translated_comments_audio, 'comment')
                voice(translated_answers_audio, 'answer')

                for language in project_configs.languages:
                    make_video(translated_titles_text[language], translated_comments_text[language],
                               translated_answers_text[language], link, language, name_index, j)

            name_index += 1

    remove_production_files()

    names, indexes, links = make_names(TITLES, flags)
    additional.write_names(names, indexes, links)

    additional.write_date()
    additional.write_name_index(name_index)


if __name__ == '__main__':
    main()
