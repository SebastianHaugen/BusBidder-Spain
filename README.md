# BusBidder-Spain
A command-line application that ranks and books bus offers from Madrid to fifteen Spanish destinations. Five fictional bus companies offer trips with different prices, departure times, durations and fare conditions. The traveller enters their requirements and chooses a traveller profile. The program removes offers that break a hard constraint, ranks the rest with a weighted score, explains the top offer, and lets the traveller book seats.

Final project for ACIT4420 – Problem-Solving with Scripting, OsloMet.

## Requirements

- Python 3.12 or newer
- No third-party packages are needed to run the application (standard library only)
- `pytest` is needed to run the tests (see `requirements.txt`)

## Setup

From the repository root:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

python -m pip install -e .
python -m pip install -r requirements.txt
```

`pip install -e .` installs the `busbidder` package in editable mode, so it can be imported from anywhere, including the tests.

## Running the program

```bash
python -m busbidder
```

The program asks for:

1. a destination
2. the earliest and latest departure date (`YYYY-MM-DD`; the dataset covers 2026-07-12 to 2026-07-14)
3. the number of seats, maximum price, whether the ticket must be changeable and the maximum number of transfers
4. a traveller profile

It then shows the offers that were filtered out and why, the ranked offers with their criterion scores, an explanation of the top offer, and finally lets you book one. Payment is simulated; no payment information is collected.

**Example input:** Malaga, 2026-07-12 to 2026-07-14, 1 seat, max €50, changeable ticket required, max 1 transfer, Balanced traveller.

Press `Ctrl+C` at any prompt to exit.

## Running the tests

```bash
python -m pytest
```

Add `-v` to list every test. The tests cover normal, invalid, missing-data and boundary cases for loading, filtering, scoring and booking. They use temporary files and never modify the data in this repository.

## Project structure

```
BusBidder-Spain/
├── config/
│   └── profiles.json          # traveller profiles: preferred time and weights
├── data/
│   ├── companies.json         # the five bus companies
│   ├── destinations.json      # the fifteen destinations
│   ├── offers.csv             # small hand-written dataset incl. invalid rows
│   └── offers_full.csv        # generated dataset used by the program
├── output/
│   ├── bookings.json          # created when the first booking is made
│   ├── logs/busbidder.log     # validation and booking events
│   └── examples/              # saved example runs used in the report
├── scripts/
│   └── generate_data.py       # seeded generator for offers_full.csv
├── src/busbidder/
│   ├── __main__.py            # entry point for `python -m busbidder`
│   ├── cli.py                 # command-line interface
│   ├── models.py              # Company, Offer, FareConditions, TravelRequest,
│   │                          # TravellerProfile, Booking
│   ├── loading.py             # reading and validating data files
│   ├── filtering.py           # hard-constraint filtering
│   ├── booking.py             # seat checks, references, saving bookings
│   ├── exceptions.py          # custom exception hierarchy
│   ├── logging_setup.py       # log file configuration
│   └── scoring/
│       ├── registry.py        # @criterion decorator registry
│       ├── criteria.py        # price, duration, departure time, flexibility
│       ├── ranker.py          # weighted ranking with tie-breaking
│       └── explain.py         # explanation of the top offer
├── tests/                     # pytest test suite
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Data

The offer data is synthetic. `scripts/generate_data.py` creates one offer per company, destination and day (12–14 July 2026), 225 offers in total, using rules derived from each company's profile. The random seed is fixed (42), so the generated file is identical on every run:

```bash
python scripts/generate_data.py
```

Invalid records (for example a negative price, an unknown company or destination, arrival before departure, or a duplicate ID) are rejected individually and written to the log file. A missing or unreadable data file stops the program with a clear error message.

## Output files

- **`output/bookings.json`**: all bookings. Seats left on an offer are calculated from this file, so the source data is never changed. **Delete this file to reset all bookings.**
- **`output/logs/busbidder.log`**: rejected records, load summaries and booking events. New runs are appended.

Both files are created automatically and are not tracked by Git.