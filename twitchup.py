import argparse
import logging
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
    user_agent=f"{sys.platform}:twitchup:0.2.0 (by /u/Volcyy)"
)

logging.basicConfig(format='%(asctime)s | %(name)-10s | %(levelname)-8s | %(message)s')
logging.getLogger('urllib3.connectionpool').setLevel(logging.WARN)
logging.getLogger('prawcore').setLevel(logging.WARN)
log = logging.getLogger('twitchup')

COMMAND_RE = re.compile(r'twitchup\((\w+)\)')
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
            log.info(f'Sleeping for {sleep_seconds} as no requests are left in this time period.')
            time.sleep(sleep_seconds)

        response.raise_for_status()
        response_json = response.json()

        if response_json['data']:
            return response_json['data'][0]
        return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--log-level',
        help="Level to emit logging output at.",
        default='INFO',
        choices=('DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
    )
    args = parser.parse_args()
    log.setLevel(args.log_level)

    sidebars = {}
    for template in os.listdir('templates'):
        with open(f'templates/{template}', 'r') as f:
            subreddit_name = template.rstrip('.md')
            sidebars[subreddit_name] = f.read()
            log.info(f"Obtained template for /r/{subreddit_name}.")

    twitch = TwitchClient()
    streams = {
        stream_name: twitch.get_stream(stream_name)
        for stream_name in {
            match.group(0).lstrip('twitchup(').rstrip(')')
            for sidebar in sidebars.values()
            for match in COMMAND_RE.finditer(sidebar)
        }
    }
    log.info(f"Loaded stream information for {len(streams)} streams.")

    for subreddit_name, sidebar in sidebars.items():
        for match in COMMAND_RE.finditer(sidebar):
            stream_name = match.group(0).lstrip('twitchup(').rstrip(')')
            if streams[stream_name] is not None:
                link_title = 'twitch-online'
            else:
                link_title = 'twitch-offline'

            markdown_link = f"[{stream_name}](https://twitch.tv/{stream_name} '{link_title}')"
            invocation = f'twitchup({stream_name})'
            sidebar = sidebar.replace(invocation, markdown_link)
            log.debug(f"Replaced `{invocation}` with `{markdown_link}`.")

        mod_relationship = reddit.subreddit(subreddit_name).mod
        old_description = mod_relationship.settings()['description']

        # Only update the sidebar if we made any actual changes.
        if sidebar != old_description:
            mod_relationship.update(description=sidebar)
            log.info(f"Updated sidebar on {subreddit_name} with new stream data.")
        else:
            log.info(f"Omitting update on {subreddit_name} as no changes would be done.")

    log.info("Done.")
