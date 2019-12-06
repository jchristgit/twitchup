import argparse
import contextlib
import itertools
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from urllib.request import Request, urlopen

import praw


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


def get_stream_information(name: str):
    request = Request(
        url=f"https://api.twitch.tv/helix/streams?user_login={name}",
        headers={'Client-Id': os.environ['TWITCH_CLIENT_ID']}
    )
    with urlopen(request) as response:
        if response.getcode() == 429:
            reset_at = float(response.headers['Ratelimit-Reset'])
            sleep_for = reset_at - time.time()
            log.info("Hit ratelimit, waiting for %.2f seconds before retry.", sleep_for)
            time.sleep(sleep_for)
            return get_stream_information(name)

        elif response.getcode() != 200:
            raise ValueError(f"unexpected code %d, response %r", response.getcode(), response.read())
        streams = json.load(response)
        if streams['data']:
            return streams['data'][0]
        return None
        

def render_template(template: str, streams: dict) -> str:
    for match in COMMAND_RE.finditer(template):
        stream_name = match.group(0)[9:-1]
        if streams[stream_name] is not None:
            link_title = 'twitch-online'
        else:
            link_title = 'twitch-offline'

        markdown_link = f"[{stream_name}](https://twitch.tv/{stream_name} '{link_title}')"
        invocation = f'twitchup({stream_name})'
        log.debug("Replaced %r with %r.", invocation, markdown_link)
        template = template.replace(invocation, markdown_link)
    return template


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-l',
        '--log-level',
        help="Level to emit logging output at.",
        default='INFO',
        choices=('DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
    )
    parser.add_argument(
        '-t',
        '--template-directory',
        help="Where to find templates.",
        default='templates'
    )
    args = parser.parse_args()
    log.setLevel(args.log_level)

    sidebars = {}
    widgets = {}
    template_dir = Path(args.template_directory)
    for subreddit_directory in template_dir.iterdir():
        subreddit_name = subreddit_directory.name
        subreddit_templates = template_dir / subreddit_name

        # ask for forgiveness, not permission.
        with contextlib.suppress(FileNotFoundError):
            sidebar_path = subreddit_templates / 'sidebar.md'
            sidebars[subreddit_name] = sidebar_path.read_text()
            log.info("Obtained sidebar template for /r/%s.", subreddit_name)

        with contextlib.suppress(FileNotFoundError):
            widget_path = subreddit_templates / 'widget.md'
            widgets[subreddit_name] = widget_path.read_text()
            log.info("Obtained widget template for /r/%s.", subreddit_name)

    streams = {
        stream_name: get_stream_information(stream_name)
        for stream_name in {
            match.group(0)[9:-1]
            for template in itertools.chain(sidebars.values(), widgets.values())
            for match in COMMAND_RE.finditer(template)
        }
    }
    log.info("Loaded stream information for %d streams.", len(streams))

    for subreddit_name, template in sidebars.items():
        sidebar = render_template(template, streams)
        mod_relationship = reddit.subreddit(subreddit_name).mod
        old_description = mod_relationship.settings()['description']

        # Only update the sidebar if we made any actual changes.
        if sidebar != old_description:
            mod_relationship.update(description=sidebar)
            log.info("Updated sidebar on %r with new stream data.", subreddit_name)
        else:
            log.info("Omitting sidebar update on %r as no changes would be done.", subreddit_name)

    for subreddit_name, template in widgets.items():
        rendered = render_template(template, streams)
        for widget in reddit.subreddit(subreddit_name).widgets.sidebar:
            if isinstance(widget, praw.models.TextArea):
                if widget.shortName != 'Streams':
                    log.info("Skipping non-stream text area %r on %r.", widget.shortName, subreddit_name)

                elif widget.text == rendered:
                    log.info(
                        "Omitting widget update on %r as no changes would be done.",
                        subreddit_name
                    )

                else:
                    try:
                        widget.mod.update(text=rendered)
                    except Exception as err:
                        log.exception(
                            "Unable to update sidebar widget on %r:",
                            subreddit_name,
                            exc_info=err
                        )
                    else:
                        log.info("Rendered sidebar update on %r.", subreddit_name)

    log.info("Done.")
