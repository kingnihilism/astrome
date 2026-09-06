# Astro Me

Astro Me is a private desktop archive for one user's personal astrology charts. Astrolog remains the calculation and reference tool; Astro Me provides a simpler place to organize, search, read, and annotate the results.

## Version One

V1 intentionally does not calculate charts. It provides five focused sections:

- Natal Chart
- Selected Asteroids
- Solar Returns
- Persona Charts
- Notes

Every section supports adding, editing, duplicating, deleting, and searching records. Data is stored locally in `data/astro_me.json` and never leaves the computer unless the user deliberately backs up or commits that file.

## Run on Windows

1. Install [Python 3](https://www.python.org/downloads/) if it is not already installed. During installation, enable **Add Python to PATH**.
2. Download or clone this repository.
3. Double-click `run_astro_me.bat`.

No third-party Python packages are required.

## Data privacy

This repository includes an empty starter data file. If the repository will be public, keep personal interpretations and private notes out of GitHub. A future version will separate private working data from the tracked example file.

## V1 boundaries

- One user only
- Personal charts only
- Manual entry from Astrolog
- Local JSON storage
- No synastry, other people's charts, or event charts
- No built-in astrology calculations

## Suggested next steps

1. Enter the core natal placements.
2. Improve each section's fields based on real use.
3. Add JSON backup and restore.
4. Import Astrolog text exports.
5. Package Astro Me as a Windows `.exe`.
