# Changelog
All notable changes will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project aims to adhere to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## [0.2.0] - 2018-09-15
### Added
- The subreddit sidebar is no longer updated if no changes would be made by an update.
- Now supports multiple templates.
- Added a `Dockerfile`.
- Added logging of noteworthy events.

### Changed
- The project now uses `Pipfile` instead of `pyproject.toml`.

## [0.1.1] - 2018-05-10
### Fixed
- Fixed RegEx matching for the `twitchup` matching more than wanted.

## [0.1.0] - 2018-05-09
### Added
- The `twitchup.py` script, providing basic stream status fetching & sidebar updates.
- `CHANGELOG.md` to document notable changes to the project.
- `README.md` with setup instructions and basic usage details.
- `pyproject.toml` and `pyproject.lock` files for local setup through `poetry`.


[Unreleased]: https://github.com/olivierlacan/keep-a-changelog/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/Volcyy/twitchup/compare/v0.1.0...v1.1.1
