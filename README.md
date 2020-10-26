# Royce's Bot
## A Discord Bot created by Royce C.
- Includes cogs with their corresponding commands to support your Discord server.

# Changelog - Royce's Discord Bot
All notable changes to this project will be documented in this file.

## [2.1.9] - 2020-08-27 - Removed external cog folder
### Changed
- Upcoming.txt (embed) to the Formula 1 Rolex Belgian Grand Prix 2020

### Removed
- Cog folder outside of main

## [2.1.8] - 2020-08-15 - Fixed general help embed
### Fixed
- General page not displaying when going to the previous page.
- Incorrect page numbers shown in the help embed.

## [2.1.7] - 2020-08-15 - Fixed help embed
### Added
- 6th missing page in nhelp embed (utility)
- pytz to requirements.txt

### Fixed
- Help embed pages showing incorrect commands if cog were unloaded

## [2.1.6] - 2020-08-14 - Removed DiscordBot.py outside main
### Removed
- DiscordBot.py copy outside \main

## [2.1.5] - 2020-08-14 - Removed external files from main
### Removed
- Files copied within \main (.txt)

## [2.1.4] - 2020-08-14 - Updated requirements.txt
### Changed
- youtube_dl requirements [2020.7.28] for Heroku hosting

## [2.1.3] - 2020-08-14 - Moderation prefixes
### Fixed
- Incorrect prefixes being displayed

## [2.1.2] - 2020-08-14 - F1 Bug fixes/updates
### Added
- New tracks added to the F1 2020 Calendar
- Mugello Circuit added
- Sochi Autodrom added
- Nürburgring added
- Portimão Circuit added
- Latin-1 encoding

### Changed
- Tracks embed to respect Discord's character limits (title/name)
- Upcoming embed (Spanish GP)

### Removed
- Triple quoted strings of unused functions

### Fixed
- Incorrect prefixes displayed when multiple were in use (list[0])
- Cut-off circuit names in upcoming setup and edit embeds
- Encoding errors for tracks with latin characters
- Typos (F1 cog)

## [2.1.1] - 2020-08-14 - Removed .txt files
### Removed
- External .txt files that weren't in use
- mutedids.txt
- muted.txt
- prefix.txt

## [2.1.0] - 2020-08-13 - F1 cog
### Added
- F1 cog for the fans

F1 cog
- Set timezone command [from the TZ database]
- Timezone command to display current timezone set
- Upcoming embed: view the upcoming race weekend schedule; adjusted to either the track times or your local time (if set)
- Set upcoming embed command
- Edit previous upcoming embed command via message ID to set it to the current one e.g. fixed embed in channel
- Track command to view all information on a particular F1 track (on the current season/year's calendar)
- Tracks command to view all available tracks to display using the track command

## [2.0.0] - 2020-08-13 - Update on DiscordBot.py
### Added
- Embeds, embeds and embeds.
- Delete pre-existing custom prefixes command
- Server info command to view information about the server e.g. member status, channels, boosts
- Status embed that displays whether or not a cog has been loaded (for use)
- Multi-page nhelp embed to view all avialable commands in one embed
- "General" commands when using nhelp command
- Extra, more detailed error embeds 
- Basic rules embed that can have rules referenced individually
- Prefix reading/writing functionality when the bot joins/leaves a server

Utility cog
- Betting system: bet on user finishing times (in any game) and receive the winner via given winning time.
- Bet command to submit an entry (minutes/seconds)
- Clear bets command to remove all entries for a new round
- Winner command via inputted winning time to determine closest bet
- Bets list command to view all bets for the current round from every user

### Changed
- DiscordBot.py to be more legible and structured: blank lines, comments, etc.
- Prefix command to be more user friendly and customisable (stored via JSON)
- Prefix command to include the list of prefixes for the server if no arguments are given

### Removed
- Unnecessary comments
- Test embed
- Cog status updates via print statements/terminal

### Fixed
- youtube_dl video format error [updated 2020.7.8]

## [1.1.2] - 2020-05-27 - Help command/cog bug fixes
### Fixed
- Cog errors causing the nhelp display to malfunction

## [1.1.1] - 2020-05-27 - Heroku hosting
### Added
- Heroku 24/7 hosting functionality

### Changed
- Where files are stored in order to be run via Heroku

## [1.1.0] - 2020-04-17 - Music and Moderation update
### Added
- Queue command to add songs to current queue to be played after a song has finished
- View queue command 
- Pause command
- Resume command
- Stop command: clears session queue and stops the music

### Changed
- Available cogs info displayed to embeds
- Moderation commands to be more robust and orthodox
- How mutes are recorded, logged and removed

### Fixed
- FileNotFoundError to AttributeError [line 304]

## [1.0.2] - 2020-04-14 - Music
### Added
- Music cog/extension
- Music cog to cogs list

Music
- Join current (user) VC command
- Leave current (user) VC command
- Play command: Downloads .mp3 file via YouTube (given URL) and plays music in joined VC [using youtube_dl]

### Changed
- Except statements to include specific errors
- Cog variables names to improve legibility

## [1.0.1] - 2020-04-13 - Cogs
### Added
- 3 cogs/extensions: fun, moderation, utility

General
- (Change) prefix command
- Users command to view number of users in server
- Load cog command
- Unload cog command
- View cogs command
- Improved/refined help command containing brief descriptions as well as in-depth descriptions per cog.

Fun
- 8ball command

Moderation
- Mute command (basic)
- Unmute command (basic)
- Voice chat mute command (add role)

Utility
- Unorthodox ping command to check users ping (via Discord)

## [1.0.0] - 2020-04-13 - Initial commit
### Added
- DiscordBot.py (main) containing general commands
- 3 cogs/extensions: fun, moderation, utility

General
- (Change) prefix command
- Users command to view number of users in server
- Load cog command
- Unload cog command
- View cogs command
- Improved/refined help command containing brief descriptions as well as in-depth descriptions per cog.
