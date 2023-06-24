# Changelog
All notable changes will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project aims to adhere to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## v0.4.0 - 2023-06-24
### Added
- The new required `OWNER_NAME` configuration setting.
- Template custom widgets with matching title if present.
- Support for using the new OAuth-based Twitch API.

### Fixed
- Gracefully handle subreddits with missing permissions.

### Changed
- Updated requirements to praw 7.6.0. The previous version should still work,
  this was mainly bumped because Debian stable bumped its version.

### Removed
- Obsolete requirement for the `SUBREDDIT_NAME` variable. The `templates`
  directory is now used for this.


## v0.3.1 - 2019-12-06
### Added
- Added the `--template-directory` argument.


## v0.3.0 - 2019-12-06
### Added
- Now allows changing the log level via `argparse`.
- Support for widgets. Each subreddit in the template directory now is its own
  directory, and can contain a `sidebar.md` file to continue templating the old
  template, and a `widget.md` file to template a text area widget with the title
  "Streams".

### Fixed
- Fixed command invocation sometimes turning up weird results.

### Removed
- `pipenv` in favour of plain `pip` and `requirements.txt`.
- Direct dependency to `requests`.


## v0.2.0 - 2018-09-15
### Added
- The subreddit sidebar is no longer updated if no changes would be made by an update.
- Now supports multiple templates.
- Added a `Dockerfile`.
- Added logging of noteworthy events.

### Changed
- The project now uses `Pipfile` instead of `pyproject.toml`.


## v0.1.1 - 2018-05-10
### Fixed
- Fixed RegEx matching for the `twitchup` matching more than wanted.


## v0.1.0 - 2018-05-09
### Added
- The `twitchup.py` script, providing basic stream status fetching & sidebar updates.
- `CHANGELOG.md` to document notable changes to the project.
- `README.md` with setup instructions and basic usage details.
- `pyproject.toml` and `pyproject.lock` files for local setup through `poetry`.

<!-- vim: set textwidth=80 sw=2 ts=2: -->
