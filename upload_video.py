import moviepy.editor as me
import datetime
import os
import socket
import time
import pyautogui as p
from googletrans import Translator
from instabot import Bot

import additional
import project_configs
import video_description

source_folder = project_configs.source_folder
temporary_files_folder = project_configs.temporary_files_folder
default_folder = project_configs.default_folder


def login_youtube(language):
    """
    YouTube login macro

    :param language: given language

    :return:
    """

    os.system('open -a "Google Chrome"')  # Open Chrome
    time.sleep(1)
    p.hotkey('command', 'n', interval=0.2)  # Open new tab
    p.typewrite('https://www.youtube.com/channel_switcher')  # Go to channel switcher
    p.press('enter')
    time.sleep(5)
    p.click(x=project_configs.youtube_macro[language]['x'], y=project_configs.youtube_macro[language]['y'])  # Choose channel
    time.sleep(5)
    p.hotkey('command', 'w', interval=0.2)
    p.hotkey('command', 'n', interval=0.2)  # Open new tab
    p.typewrite('studio.youtube.com')  # Go to YouTube studio
    p.press('enter')
    time.sleep(5)


def login_tiktok(language):
    """
    TikTok login macro

    :param language: given language

    :return:
    """

    login = additional.read_login('tiktok')

    command = f'sudo systemsetup -setusingnetworktime off -s'
    additional.execute_sudo_command(command)

    os.system('open -a "Google Chrome"')  # Open Chrome
    time.sleep(1)

    p.hotkey('command', 'n', interval=0.2)  # Open new tab
    p.typewrite('https://www.tiktok.com/upload')  # Go login page (automatically goes to upload after logining
    p.press('enter')
    time.sleep(5)

    p.click(712, 416)  # Navigate through login page
    time.sleep(1)
    p.click(791, 261)
    time.sleep(1)
    p.click(553, 303)
    p.typewrite(login[language]['login'])  # Input login
    p.click(553, 352)
    p.typewrite(login[language]['password'])  # Input password
    p.press('enter')
    time.sleep(5)
    p.press('enter')
    time.sleep(20)


def login_instagram(language):
    """
    Instagram login macro

    :param language: given language

    :return:
    """

    pass


def join_outro(platform, language, video_file):
    """
    Joins video and outro

    :param platform: given platform
    :param language: given language
    :param video_file: given video_file

    :return: output_file
    """

    output_file = f'{default_folder}/output/output.mpg'
    os.system(f'cat {video_file} {project_configs.platforms[platform]["mpg_path"]} | ffmpeg -f mpeg -i - -qscale 0 -vcodec mpeg4 {output_file} -y')


def make_title(name, link, counter, language):
    """
    Creates title with a given name, counter and tag

    :param name: given name
    :param link: given link
    :param counter: given counter
    :param language: given language

    :return:
    """

    translator = Translator()

    translated_name = translator.translate(name, language, 'en').text

    tags = " #" + " #".join(video_description.tags[link].split(',')[:-1])
    title = f'{counter} {translated_name}{tags}'

    return title


def make_description(name, link, language):
    """
    Creates description of a video with a given name and tags

    :param name: given name
    :param link: given link
    :param language: given language

    :return:
    """
    translator = Translator()

    translated_name = translator.translate(name, language, 'en').text
    translated_description = translator.translate(video_description.description[link], language, 'en').text

    tags = "#" + " #".join(video_description.tags[link].split(',')[:-1])
    description = f'{translated_name}\n\n{translated_description}\n\n{tags}'

    return description


def make_tags(link):
    """
    Creates tags string

    :param link: given link

    :return:
    """

    return video_description.tags[link]


def reformat_date_youtube(upload_date_time):
    """
    Reformates date to be used in YouTube macro

    :param upload_date_time: datetime object

    :return:
    """

    month = project_configs.month[upload_date_time.month]
    day = upload_date_time.day
    year = upload_date_time.year
    hour = upload_date_time.hour
    minute = upload_date_time.minute

    upload_time = f'{hour}:{minute}'
    upload_date = f'{month} {day}, {year}'

    return upload_date, upload_time


def upload_youtube(title, description, tags, upload_date_time, language):
    """
    YouTube upload macro

    :param title: given title
    :param description: given description
    :param tags: given tags
    :param upload_date_time: given datetime object
    :param language: given language

    :return:
    """

    p.click(1302, 138)  # Press upload video
    p.click(1286, 181)
    time.sleep(1)

    p.click(720, 418)  # Press the big arrow
    time.sleep(1)

    time.sleep(0.2)
    p.click(388, 239)  # Choose folder and file
    p.press('1')
    time.sleep(0.5)
    p.press('enter')
    time.sleep(5)

    p.click(535, 336)  # Input information about video (first page)
    p.scroll(-300)
    p.click(299, 608)
    p.click(331, 704)
    p.scroll(-20)
    time.sleep(1)
    p.click(337, 548)
    time.sleep(1)
    p.typewrite(tags)
    p.scroll(400)
    p.click(522, 540)
    p.typewrite(description)
    p.click(533, 404)
    p.hotkey('command', 'a', interval=0.2)
    p.typewrite(title)

    p.click(1157, 828)  # Move to forth page
    p.click(1157, 828)
    p.click(1157, 828)

    upload_date, upload_time = reformat_date_youtube(upload_date_time)

    p.click(352, 586)  # Input date
    p.click(323, 715)
    p.click(428, 570)
    p.hotkey('command', 'a', interval=0.2)
    p.write(upload_date)
    p.press('enter')

    p.moveTo(619, 576)  # Input time
    p.mouseDown()
    p.moveTo(534, 576)
    p.mouseUp()
    p.write(upload_time)

    p.click(1139, 833)  # End upload
    time.sleep(10)

    p.click(931, 642)  # Return to YouTube Studio


def reformat_date_tiktok(upload_date_time):
    """
    Reformates date to be used in TikTok upload macro

    :param upload_date_time: datetime object

    :return:
    """

    year = upload_date_time.year % 100
    month = upload_date_time.month
    day = upload_date_time.day
    hour = upload_date_time.hour
    minute = upload_date_time.minute

    upload_date = ''

    for i in [month, day, hour, minute]:
        if i < 10:
            upload_date += f'0{i}'
        else:
            upload_date += f'{i}'

    upload_date += f'{year}'

    return upload_date


def upload_tiktok(title, description, tags, upload_date_time, language):
    """
    TikTok upload macro

    :param title: given title
    :param description: given description
    :param tags: given tags
    :param upload_date_time: given datetime object
    :param language: given language

    :return:
    """

    upload_date = reformat_date_tiktok(upload_date_time)

    command = f'sudo date {upload_date} -s'
    additional.execute_sudo_command(command)

    p.hotkey('command', 'shift', 'r', interval=0.2)
    time.sleep(10)
    p.scroll(10000)
    time.sleep(0.5)
    p.scroll(-3)
    time.sleep(0.5)
    p.click(830, 722)  # Set up copyright check
    p.click(802, 671)  # Set up date

    p.click(1291, 57)  # Turn on VPN (Browsec)
    time.sleep(0.5)
    p.click(1148, 362)
    time.sleep(0.5)
    p.press('esc')

    p.click(357, 588)  # Click upload

    time.sleep(1)
    p.click(388, 239)  # Choose folder and file
    time.sleep(1)
    p.press('1')
    time.sleep(1)
    p.press('enter')
    time.sleep(3)

    time.sleep(180)

    p.click(582, 228)
    p.hotkey('command', 'a', interval=0.2)
    p.typewrite(title)

    p.scroll(-3)
    time.sleep(1)
    p.click(792, 809)

    time.sleep(10)
    p.click(742, 557)

    p.click(1291, 57)  # Turn off VPN
    time.sleep(0.5)
    p.click(1148, 362)
    time.sleep(0.5)
    p.press('esc')


def upload_instagram(title, description, tags, upload_date_time, language):
    """
    Instagram upload macro

    :param title: given title
    :param description: given description
    :param tags: given tags
    :param upload_date_time: given datetime object
    :param language: given language

    :return:
    """

    login_info = additional.read_login('instagram')

    login = login_info[language]['login']
    password = login_info[language]['password']
    video = f'{default_folder}output/output.mpg'

    bot = Bot()
    bot.login(username=login, password=password)
    bot.upload_video(video, caption=title)


def logout_tiktok():
    """
    TikTok logout macro

    :return:
    """

    p.click(1398, 145)
    time.sleep(0.5)
    p.click(1261, 457)
    time.sleep(3)
    p.hotkey('command', 'w', interval=0.2)


def logout_youtube():
    """
    YouTube logout macro

    :return:
    """

    time.sleep(5)
    p.hotkey('command', 'w', interval=0.2)


def logout_instagram():
    """
    Instagram logout macro

    :return:
    """

    pass


def main():
    print("Make sure your Google in fullscreen")
    input()

    res = additional.check_files()

    if res == 2:
        print("No TikTok login file found")
        print("Exiting...")
        return

    if res == 3:
        print("No SUDO password file found")
        print("Exiting...")
        return

    if res == 4:
        print("No SUDO password file found")
        print("Exiting...")
        return

    socket.setdefaulttimeout(100000)

    upload_date_time = additional.read_date()
    name_index = additional.read_name_index()
    names, indexes, links = additional.read_names()
    count, i_prev, j_prev = additional.read_temp()
    shift = additional.read_shift()

    for platform in project_configs.platforms:
        for language in project_configs.languages:

            globals()[f'login_{platform}'](language)

            daily_counter = 0
            flag = 0

            for i in range(i_prev[platform][language], name_index):
                name = names[i]
                link = links[i]
                index = indexes[i]

                for j in range(j_prev[platform][language], index):
                    videoname = f'{i}_{j}.mpg'
                    video_file = f'{default_folder}{language}/videos/{videoname}'

                    if not os.path.exists(video_file):
                        continue

                    clip = me.VideoFileClip(video_file)

                    if clip.duration + project_configs.outro_length > project_configs.platforms[platform][
                        'max_duration']:
                        continue

                    if daily_counter == project_configs.platforms[platform]['daily_limit'][language]:
                        flag = 1
                        j_prev[platform][language] = j
                        i_prev[platform][language] = i
                        break

                    join_outro(platform, language, video_file)

                    title = make_title(name, link, count[platform][language][link], language)
                    description = make_description(name, link, language)
                    tags = make_tags(link)

                    globals()[f'upload_{platform}'](title, description, tags, upload_date_time[platform][language], language)

                    count[platform][language][link] += 1
                    daily_counter += 1
                    upload_date_time[platform][language] += datetime.timedelta(seconds=shift[platform][language])

                if flag:
                    break

                j_prev[platform][language] = 0
                i_prev[platform][language] = i+1

                j_prev[platform][language] = 0

            globals()[f'logout_{platform}']()

    additional.write_temp(i_prev, j_prev, count)
    additional.write_date(upload_date_time)

    command = f'sudo systemsetup -setusingnetworktime on -s'
    additional.execute_sudo_command(command)


if __name__ == '__main__':
    main()
