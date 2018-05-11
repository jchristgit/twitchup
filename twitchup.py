import os
import re
import sys
import time

import praw
import requests


reddit = praw.Reddit(
    client_id=os.environ['REDDIT_CLIENT_ID'],
    client_secret=os.environ['REDDIT_CLIENT_SECRET'],
    username=os.environ['REDDIT_USERNAME'],
    password=os.environ['REDDIT_PASSWORD'],
    user_agent=f"{sys.platform}:twitchup:0.1.1 (by /u/Volcyy)"
)
COMMAND_RE = re.compile(r'(?<=twitchup\()(.*?)(?=\))')
SUBREDDIT_NAME = os.environ['SUBREDDIT_NAME']


class TwitchClient:
    STREAM_ENDPOINT = "https://api.twitch.tv/helix/streams"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers['Client-ID'] = os.environ['TWITCH_CLIENT_ID']

    def get_stream(self, stream_login: str):
        response = self.session.get(f"{self.STREAM_ENDPOINT}?user_login={stream_login}")

        if response.headers['Ratelimit-Remaining'] == 0:
            sleep_seconds = response.headers['Ratelimit-Remaining'] - time.time()
            print(f'sleeping for {sleep_seconds} as no requests are left in this time period')
            time.sleep(sleep_seconds)

        response.raise_for_status()
        response_json = response.json()

        if response_json['data']:
            return response_json['data'][0]
        return None


if __name__ == '__main__':
    with open('template.md', 'r') as f:
        sidebar = f.read()

    twitch = TwitchClient()

    for match in COMMAND_RE.finditer(sidebar):
        stream_name = match.group(0).strip('()')
        stream_data = twitch.get_stream(stream_name)
        if stream_data is not None:
            link_title = 'twitch-online'
        else:
            link_title = 'twitch-offline'

        markdown_link = f"[{stream_name}](https://twitch.tv/{stream_name} '{link_title}')"
        sidebar = sidebar.replace(f'twitchup({stream_name})', markdown_link)

    mod_relationship = reddit.subreddit(SUBREDDIT_NAME).mod
    old_description = mod_relationship.settings()['description']

    # Only update the sidebar if we made any actual changes.
    if sidebar != old_description:
        mod_relationship.update(description=sidebar)
    else:
        print('not updating sidebar as there is no difference to the current one')
