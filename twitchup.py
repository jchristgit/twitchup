import argparse
import contextlib
import itertools
import json
import logging
import os
import re
import sys
import time
from typing import Generator, List, Set
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import praw
from prawcore import NotFound


reddit = praw.Reddit(
    client_id=os.environ['REDDIT_CLIENT_ID'],
    client_secret=os.environ['REDDIT_CLIENT_SECRET'],
    username=os.environ['REDDIT_USERNAME'],
    password=os.environ['REDDIT_PASSWORD'],
    user_agent=f"{sys.platform}:twitchup:0.4.0 (by /u/{os.environ['OWNER_NAME']})",
)

logging.basicConfig(
    format=os.getenv(
        'LOG_FORMAT', '%(asctime)s | %(name)-10s | %(levelname)-8s | %(message)s'
    )
)
logging.getLogger('urllib3.connectionpool').setLevel(logging.WARN)
logging.getLogger('prawcore').setLevel(logging.WARN)
log = logging.getLogger('twitchup')

COMMAND_RE = re.compile(r'twitchup\((\w+)\)')
SUBREDDIT_NAME = os.environ['SUBREDDIT_NAME']


def chunks(over: List[str], size: int) -> Generator[List[str], None, None]:
    for i in range(0, len(over), size):
        yield over[i : i + size]


def fetch_access_token() -> str:
    request = Request(
        url=(
            f"https://id.twitch.tv/oauth2/token"
            f"?client_id={os.environ['TWITCH_CLIENT_ID']}"
            f"&client_secret={os.environ['TWITCH_CLIENT_SECRET']}"
            f"&grant_type=client_credentials"
        ),
        method='POST',
    )

    with urlopen(request) as response:
        result = json.load(response)
    return result['access_token']


def load_online(names: List[str], access_token: str):
    login_params = '&'.join(f'user_login={login}' for login in names)
    request = Request(
        url=f"https://api.twitch.tv/helix/streams?first=100&{login_params}",
        headers={
            'Authorization': f'Bearer {access_token}',
            'Client-Id': os.environ['TWITCH_CLIENT_ID'],
        },
    )
    try:
        with urlopen(request) as response:
            if response.getcode() != 200:
                raise ValueError(
                    f"unexpected code %d, response %r",
                    response.getcode(),
                    response.read(),
                )
            streams = json.load(response)
            return {stream['user_name'] for stream in streams.get('data', ())}
    except HTTPError as response:
        if response.code == 429:
            reset_at = float(response.headers['Ratelimit-Reset'])
            sleep_for = reset_at - time.time()
            log.info("Hit ratelimit, waiting for %.2f seconds before retry.", sleep_for)
            time.sleep(sleep_for)
            return load_online(names)
        raise


def get_online_streams(streams: List[str], access_token: str) -> Set[str]:
    online = set()
    for logins in chunks(over=streams, size=100):
        online |= load_online(logins, access_token)
    return online


def render_template(template: str, online_streams: Set[str]) -> str:
    for match in COMMAND_RE.finditer(template):
        stream_name = match.group(0)[9:-1]
        if stream_name in online_streams:
            link_title = 'twitch-online'
        else:
            link_title = 'twitch-offline'

        markdown_link = (
            f"[{stream_name}](https://twitch.tv/{stream_name} '{link_title}')"
        )
        invocation = f'twitchup({stream_name})'
        log.debug("Replaced %r with %r.", invocation, markdown_link)
        template = template.replace(invocation, markdown_link)
    return template.strip()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-l',
        '--log-level',
        help="Level to emit logging output at.",
        default='INFO',
        choices=('DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'),
    )
    parser.add_argument(
        '-t',
        '--template-directory',
        help="Where to find templates.",
        default='templates',
    )
    args = parser.parse_args()
    log.setLevel(args.log_level)
    access_token = fetch_access_token()

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
            log.debug("Obtained sidebar template for /r/%s.", subreddit_name)

        with contextlib.suppress(FileNotFoundError):
            widget_path = subreddit_templates / 'widget.md'
            widgets[subreddit_name] = widget_path.read_text()
            log.debug("Obtained widget template for /r/%s.", subreddit_name)

    names = {
        match.group(0)[9:-1]
        for template in itertools.chain(sidebars.values(), widgets.values())
        for match in COMMAND_RE.finditer(template)
    }
    online = get_online_streams(list(names), access_token)
    log.info(
        "Loaded stream information for %d streams, %d online (%s)",
        len(names),
        len(online),
        ', '.join(online),
    )

    for subreddit_name, template in sidebars.items():
        sidebar = render_template(template, online)
        mod_relationship = reddit.subreddit(subreddit_name).mod
        try:
            old_description = mod_relationship.settings()['description']
        except NotFound:
            log.warning(
                "Cannot obtain settings for %r, are permissions available?",
                subreddit_name,
            )
        else:
            # Only update the sidebar if we made any actual changes.
            if sidebar != old_description:
                mod_relationship.update(description=sidebar)
                log.info("Updated sidebar on %r with new stream data.", subreddit_name)
            else:
                log.info(
                    "Omitting sidebar update on %r as no changes would be done.",
                    subreddit_name,
                )

    for subreddit_name, template in widgets.items():
        rendered = render_template(template, online)
        for widget in reddit.subreddit(subreddit_name).widgets.sidebar:
            if isinstance(widget, (praw.models.CustomWidget, praw.models.TextArea)):
                if widget.shortName != 'Streams':
                    log.debug(
                        "Skipping non-stream widget %r (%s) on %r.",
                        widget.shortName,
                        widget.__class__.__name__,
                        subreddit_name,
                    )

                elif widget.text == rendered:
                    log.info(
                        "Omitting widget update on %r as no changes would be done.",
                        subreddit_name,
                    )

                else:
                    try:
                        widget.mod.update(text=rendered)
                    except Forbidden:
                        log.warning(
                            "Unable to update sidebar widget on %r, forbidden.",
                            subreddit_name,
                        )
                    except Exception as err:
                        log.exception(
                            "Unable to update sidebar widget on %r:",
                            subreddit_name,
                            exc_info=err,
                        )
                    else:
                        log.info("Rendered widget update on %r.", subreddit_name)

    log.info("Done.")
