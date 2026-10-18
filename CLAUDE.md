# calendars: instructions for Claude

Public repo (caydenwe/calendars) of subscribable .ics feeds. Each feed is built from a
CSV in `data/` by `build.py`, using `calendars.toml`. The **Build calendars** Action
(`.github/workflows/build.yml`) rebuilds feeds on every push to `main` that touches
`data/`, `calendars.toml` or `build.py`, and commits the .ics itself.

The CSVs in `data/` are the only source. There are no copies elsewhere: the old
Numbers files, the Desktop/Downloads "Python Scripts" folder and the
`calendar-creation-files` scripts are retired. Never bring back a script that holds a
GitHub token.

## Hard rules

- **Never rename, move or delete a feed's `.ics` file**, or change `output` in
  `calendars.toml`. The file name is part of the subscribe URL that other people use,
  and those people can't be asked to resubscribe.
- Don't hand-edit `.ics` files. Edit the CSV and let the build regenerate them.
- The repo is public. Only put things here that the user is happy for anyone to see.
- Event identity (UID) = feed + title + start date. Changing an event's name or start
  date makes subscribers' apps drop the old event and add a new one. That's fine and
  expected, but it means alerts people set on that event are lost.

## Updating Julian's Racing (`data/julians-racing.csv`)

Feed URL (shared with many people; must never change):
`https://raw.githubusercontent.com/caydenwe/calendars/main/Julian's%20Racing%20Dates.ics`

Columns: `Race Name,Start Date,End Date,Location`

| Column | How to fill it |
|---|---|
| Race Name | The event's name **without** a trailing "Race". The build adds " Race" to every title (`Test Day` → "Test Day Race"). |
| Start Date | `D Mon YYYY`: day without a leading zero, three-letter month, four-digit year, e.g. `1 Feb 2026`, `23 Oct 2026`. |
| End Date | The **last day** of the event (inclusive), same format. For one-day events, repeat the start date (the existing rows all do). |
| Location | Circuit or venue as a person would say it, e.g. `Sydney Motorsport Park`, `GP Circuit, Eastern Creek`, `Phillip Island`. Quote it if it has a comma (a CSV writer does this for you). |

Conventions already in the data. Keep following them:
- If the user says Julian/SCMR isn't going to an event, keep it and append
  ` (SCMR Not Planning to Attend)` to the Race Name. Don't delete the row.
- Rows are in date order. Insert new rows where they belong by Start Date.
- Past events stay in the file (it's a history). Remove rows only when asked.
- Round numbers go in the name: `NSW Supersports Championship R5`.
- Same name on different dates is fine (e.g. several `Test 2 - SMSP`). The same name on
  the **same** start date is rejected as a duplicate.
- Text is UTF-8 and may contain curly quotes (`PIARC’s Island Magic`). Leave them as they are.

If a request is ambiguous (no year, "the weekend of the 12th" without a month, an
unknown venue), ask rather than guess. A wrong date in a feed many people follow is worse
than a short delay.

### Workflow

1. `git pull --ff-only` in this repo (the user also edits on GitHub directly).
2. Edit the CSV with a CSV-aware tool (Python `csv`), not by string-splicing lines that
   contain commas.
3. Run `python3 build.py`. It must exit 0. A bad row stops it with `file line N: reason`.
4. Show the user the changed rows (`git diff data/`) and get a yes before pushing,
   because the feed goes out to other people.
5. Commit only the CSV (not the .ics; the Action builds and commits that), with a message
   like `Julian's Racing: add NSW Supersports R1 2027`, then push.
6. Wait for the Action (`gh run list --workflow build.yml -L1`; it should be
   `completed success`), then `git pull`, and confirm the live URL serves the change
   (`curl -s '<feed URL>' | grep -A3 'SUMMARY:<name>'`). raw.githubusercontent.com can
   cache for about 5 minutes.

Subscribers see the change at their app's next refresh (often hours on iPhone). The user
can force it in Calendar on the Mac with View → Refresh Calendars.

## Adding the next football season (not built yet)

The old soccer feeds were deleted. When the user asks for next season's fixtures, add
a new `[[calendar]]` entry plus a CSV. `build.py` only does all-day events today, so add
**timed events** first: an optional `time_format`/datetime column, a `duration`, and
`TZID=Australia/Sydney` with a VTIMEZONE (or UTC times). Keep all-day behaviour
unchanged for Julian's feed, and check its .ics is byte-identical after the change.

What the retired scripts did (match this unless the user says otherwise):
- CSV columns: `Round,Opposition,Home/Away,Time,Grade,Location` (`Grade` missing for
  cup comps). `Time` is like `18 Apr 2026 3:00 pm` (`%d %b %Y %I:%M %p`), local
  Australia/Sydney time. A `Time` of `TBC` means skip the row for now.
- Duration: 1 h 45 min.
- Title: `Round {Round} {Grade} vs {Opposition}`, then ` at Home` if Home/Away is
  `Home`, else ` Away`. Cup comps leave out Grade (`Round K1 vs …`). This needs a
  conditional suffix, which the template system doesn't do yet. Add a small mapping
  option rather than special-casing in code.
- Location: the ground, e.g. `Judy Masters Oval 1`. The user's spreadsheets had a
  "Fixture Locations" helper table (Team → Home Ground) for filling this in: away games
  are at the opposition's ground, home games at the club's own.
- Past competitions: IPL2 (Illawarra Premier League 2, 1st Grade, home ground Judy
  Masters Oval 1, Balgownie Rangers), the Bert Bampton cup, pre-season friendlies, and
  earlier Canberra CPL/CLO3 seasons.
- Pick a new, permanent `output` name for each new feed (e.g.
  `soccer_schedule_2027.ics`) and tell the user the subscribe URL to share.
