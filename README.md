# calendars

Subscribable calendar feeds. Each one is built from a CSV in `data/` by a GitHub Action.

## Updating a calendar

Edit the CSV in `data/` (in GitHub's web editor or locally) and commit to `main`.
The **Build calendars** Action rebuilds the `.ics` and commits it. Subscribers pick up
the change the next time their calendar app refreshes.

If a row is wrong (a bad date, or a duplicate), the Action fails and the published
feed is left as it was. Check the Actions tab after an edit.

Dates use the `date_format` set in `calendars.toml` (e.g. `1 Feb 2026`). `End Date`
is the last day of the event and can be left blank for one-day events.

## Feeds

| Calendar | Subscribe URL |
|---|---|
| Julian's Racing | `https://raw.githubusercontent.com/caydenwe/calendars/main/Julian's%20Racing%20Dates.ics` |

Never rename a feed's `.ics` file. Its name is part of everyone's subscription link.

## Adding a calendar

Add a CSV to `data/` and a `[[calendar]]` entry to `calendars.toml`. Run
`python3 build.py` to check it locally (standard library only, Python 3.11+).
