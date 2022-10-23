import os
import moviepy.editor as me

import additional
import project_configs

default_folder = project_configs.default_folder


def calculate_total(name_index, indexes, i_prev, j_prev, master_language=None):
    """
    Counts every video created

    :param name_index: given name_index
    :param indexes: given indexes array (stores the amount of videos every title has)
    :param master_language: if given uses this language to track deleted videos

    :return: total
    """

    total = additional.make_null_dict([project_configs.platforms, project_configs.languages])
    for platform in project_configs.platforms:
        for language in project_configs.languages:
            for i in range(i_prev[platform][language], name_index):
                index = indexes[i]
                for j in range(j_prev[platform][language], index):
                        video_name = f'{i}_{j}.mpg'
                        video = f'{default_folder}{language}/videos/{video_name}'

                        if not os.path.exists(video):
                            continue

                        if master_language is not None:
                            master_video = f'{default_folder}{master_language}/videos/{video_name}'
                            if not os.path.exists(master_video):
                                continue

                        duration = me.VideoFileClip(video).duration

                        if duration + project_configs.outro_length < project_configs.platforms[platform]['max_duration']:
                            total[platform][language] += 1

    return total


def create_shift_dict(total):
    """
    Calculates shift for every type of video

    :param total: given total (dictionary)

    :return: shift
    """

    shift = additional.make_null_dict([project_configs.platforms, project_configs.languages])
    seconds_in_week = 7*24*60*60

    for platform in project_configs.platforms:
        for language in project_configs.languages:
            daily_limit = project_configs.platforms[platform]['daily_limit'][language]
            temp = seconds_in_week / (7 * daily_limit)

            if total[platform][language] < daily_limit * 7:
                temp = seconds_in_week / total[platform][language]

            shift[platform][language] = temp

    return shift


def main():
    additional.check_files()

    name_index = additional.read_name_index()
    names, indexes, links = additional.read_names()
    count, i_prev, j_prev = additional.read_temp()
    total = calculate_total(name_index, indexes, i_prev, j_prev)
    shift = create_shift_dict(total)
    additional.write_shift(shift)


if __name__ == '__main__':
    main()
