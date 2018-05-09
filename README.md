# twitchup
`twitchup` adds Twitch stream status indicators for subreddit sidebars.
It works by polling stream information from Twitch's API and then updating
a given sidebar template.

## Setup
- `git clone https://github.com/Volcyy/twitchup`
- `cd twitchup`

Set the following environment variables:
- `REDDIT_CLIENT_ID`: your reddit bot client ID
- `REDDIT_CLIENT_SECRET`: your reddit bot client secret
- `REDDIT_USERNAME` and `REDDIT_PASSWORD` for the bot account
- `TWITCH_CLIENT_ID`: your twitch app client ID (get it [here](https://dev.twitch.tv/dashboard/apps))
- `SUBREDDIT_NAME`: the subreddit to operate on

You can get the reddit credentials [here](https://www.reddit.com/prefs/apps/).
Make sure to add the bot as a moderator on the specific subreddit.

Install dependencies: `pip3 install requests praw` (or through `poetry`: `poetry install`).

## Usage
Create a file named `template.md` and place your subreddit's sidebar
(as Markdown) in there. Use `twitchup(<stream_name>)` where you want
stream information to be placed. `twitchup` generates the following:

For an online stream, `twitchup(name)` becomes:
```md
[name](https://twitch.tv/name 'stream-online')
```
and for an offline stream, `twitchup(name)` becomes:
```md
[name](https://twitch.tv/name 'stream-offline')
```

You can then apply custom styles in your subreddit's stylesheet.

To run the script, simply use `python3 twitchup.py`.


## Disclaimer
`twitchup` is not affiliated nor endorsed by Twitch.

## Credits
`twitchup` is inspired by [`twitchit`](https://github.com/jensechu/twitchit).
