# twitchup

`twitchup` adds Twitch stream status indicators for subreddit sidebars. It
works by polling stream information from Twitch's API and then updating a given
sidebar template.

## Setup

Set the following environment variables:
- `REDDIT_CLIENT_ID`: your reddit bot client ID
- `REDDIT_CLIENT_SECRET`: your reddit bot client secret
- `REDDIT_USERNAME` and `REDDIT_PASSWORD` for the bot account
- `TWITCH_CLIENT_ID`: your twitch app client ID (get it
  [here](https://dev.twitch.tv/dashboard/apps))

You can get the reddit credentials [here](https://www.reddit.com/prefs/apps/).
Make sure to add the bot as a moderator on the specific subreddit.

Install dependencies: `pip3 install -r requirements.txt`.

## Usage

Create a directory named `templates` (or any place of your liking, as specified
by the `--template-directory` switch) and create subdirectories named after the
desired subreddits in there. To template a custom or text area widget with the
title "Streams", create a file named `widget.md` in said subdirectory. For
templating the old-style sidebar, create a file named `sidebar.md` instead. You
can also create both files. Use `twitchup(<stream_name>)` where you want stream
information to be placed.  `twitchup` generates the following:

For an online stream, `twitchup(name)` becomes:
```md
[name](https://twitch.tv/name 'twitch-online')
```
and for an offline stream, `twitchup(name)` becomes:
```md
[name](https://twitch.tv/name 'twitch-offline')
```

You can then apply custom styles in your subreddit's stylesheet.

To run the script, simply use `python3 twitchup.py`.


## Disclaimer
`twitchup` is not affiliated nor endorsed by Twitch.

## Credits
`twitchup` is inspired by [`twitchit`](https://github.com/jensechu/twitchit).


<!-- vim: set textwidth=80 sw=2 ts=2: -->
