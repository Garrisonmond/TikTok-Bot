"""
Project configurations file (change params there)
"""

# Main folders
default_folder = '/Users/garrisonmond/Desktop/TikTok_Bot/'
source_folder = '/Users/garrisonmond/Desktop/TikTok_Bot/sources/'
temporary_files_folder = default_folder + 'temporary_files/'

# Temporary files
temporary_files = {
    'date_file': temporary_files_folder + 'date.txt',
    'names_file': temporary_files_folder + 'names.txt',
    'name_index_file': temporary_files_folder + 'name_index.txt',
    'temp_file': temporary_files_folder + 'temp.txt',
    'reddit_login_file': temporary_files_folder + 'reddit_login.txt',
    'not_allowed_file': temporary_files_folder + 'not_allowed.txt',
    'remove_file': temporary_files_folder + 'remove.txt',
    'shift_file': temporary_files_folder + 'shift.txt',
    'tiktok_login_file': temporary_files_folder + 'tiktok_login.txt',
    'instagram_login_file': temporary_files_folder + 'instagram_login.txt',
    'sudo_password_file': temporary_files_folder + 'sudo_password.txt',
    'nsfw_words_file': temporary_files_folder + 'nsfw_words.txt'
}

# Links configs
links = {
    "ama": {
        'link': "https://oauth.reddit.com/r/IAmA/top/?t=week",
        'check_nsfw': 0
    },
    "ask": {
        'link': "https://oauth.reddit.com/r/AskReddit/top/?t=week",
        'check_nsfw': 1
    }
}

# Languages configs
languages = {
    'en': {
        'voice': {
            'name': ['Allison'],
            'rate': [172]
        }
    }
}


# Platforms configs
platforms = {
    'youtube': {
        'daily_limit': {
            'en': 4,
            'ru': 4,
            'es': 4
        },
        'max_duration': 55,
        'mpg_path': source_folder + 'youtube.mpg',
        'CLIENT_SECRET_FILE': temporary_files_folder + 'youtube_secret.json',
        'API_NAME': 'youtube',
        'API_VERSION': 'v3',
        'SCOPES': ['https://www.googleapis.com/auth/youtube.upload']
    },
    'tiktok': {
        'daily_limit': {
            'en': 4,
            'ru': 4,
            'es': 4
        },
        'max_duration': 55*5,
        'mpg_path': source_folder + 'tiktok.mpg',
    },
    'instagram': {
        'daily_limit': {
            'en': 4,
            'ru': 4,
            'es': 4
        },
        'max_duration': 55,
        'mpg_path': source_folder + 'instagram.mpg',
    }
}

# Video creator configs
txt_params = {
    "font": 'Verdana',
    "size": [800, 0],
    "title_fontsize": 32,
    "comment_fontsize": 27,
    "bg_color": "white",
    "color": "black",
    "align": "west",
    "method": "caption"
}
offset_w, offset_h, offset_m = 200, 100, 50
multiplier = 0.9 / 1920
pause_time = 1
outro_length = 5


abbreviations = {
    'ama': "ask me anything",
    'afaik': 'as far as i know',
    'brb': 'be right back',
    'iirc': 'if i recall',
    'np': 'no problem',
    'ty': 'thank you',
    'yw': 'you are welcome',
    'wth': 'what the hell',
    'ftr': 'for the record',
    'sry': 'sorry',
    'thx': 'thanks',
    'ofc': 'of course',
    'imo': 'in my opinion',
    'imho': 'in my humble opinion',
    'idk': 'i do not know',
    'idek': 'i do not even know',
    'fyi': 'for your information',
    'jk': 'just kidding'
}

youtube_macro = {
    'ru': {
        'x': 749,
        'y': 313
    },
    'en': {
        'x': 1042,
        'y': 313
    },
    'es': {
        'x': 470,
        'y': 379
    },
    'hi': {
        'x': 788,
        'y': 382
    }
}


month = {
        1: 'Jan',
        2: 'Feb',
        3: 'Mar',
        4: 'Apr',
        5: 'May',
        6: 'Jun',
        7: 'Jul',
        8: 'Aug',
        9: 'Sep',
        10: 'Oct',
        11: 'Nov',
        12: 'Dec'
    }