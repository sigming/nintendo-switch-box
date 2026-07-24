import os
import re

from nintendo import NintendoClient
from utils import clean_game_name, convert_play_duration, update_gist, truncate_strings


def contains_japanese(text):
    """Check if text contains Japanese characters (Hiragana, Katakana, or Kanji)"""
    return bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', text))


session_token = os.environ.get('NINTENDO_SESSION_TOKEN')
github_token = os.environ.get('GH_TOKEN')
gist_id = os.environ.get('GIST_ID')

if __name__ == '__main__':
    if not session_token:
        print('Please set the session token to the environment')
        exit(1)

    print('Fetching play histories...')
    client = NintendoClient(session_token=session_token)
    play_histories = client.get_play_histories()
    if not play_histories:
        print('Failed to get play histories.')
        exit(1)

    total_games = len(play_histories['playHistories'])
    print(f'Found {total_games} games in play history')

    show_records = []
    for i in play_histories['playHistories']:
        record = {
            'title': i['titleName'],
            'played_minutes': i['totalPlayedMinutes'],
            'played_minutes_str': convert_play_duration(i['totalPlayedMinutes']),
            'played_days': i['totalPlayedDays'],
        }
        if record['played_minutes'] == 0:
            continue

        # Fallback: if title contains Japanese, try to get English name
        if contains_japanese(record['title']):
            print(f'  Fetching English name for: {record["title"]}')
            title_en = client.get_game_title(i['titleId'], region='US').get('name')
            if title_en:
                record['title'] = title_en
        record['title'] = clean_game_name(record['title'])

        show_records.append(record)
    show_records.sort(key=lambda x: x['played_minutes'], reverse=True)
    if len(show_records) == 0:
        print('No play history found.')
        exit(0)

    print(f'\nTop {min(20, len(show_records))} games by play time:')
    print('-' * 52)
    gist_content = ''
    for record in show_records[:20]:
        line = [
            truncate_strings(record['title'], 26).ljust(26),
            record['played_minutes_str'].rjust(16),
            str(record['played_days']).rjust(4) + ' days'
        ]
        line = ' '.join(line)
        print(line)
        gist_content += line + '\n'
    print('-' * 52)

    print('\nUpdating gist...')
    update_gist(gist_id, github_token, gist_content.strip())
    print('Done!')
