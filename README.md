# League of Legends Performance Analyzer

A Python and SQL analytics project that analyzes ranked League of Legends match history using the Riot Games API and MySQL. The project combines automated data collection, database storage, performance analysis, data-quality checks, and visualizations.

## Project Overview

This project retrieves up to 100 of the most recent available Ranked Solo/Duo matches for a League of Legends account, stores match data in MySQL, and analyzes gameplay performance using Python.

The analysis includes win-rate trends, champion performance, KDA, CS per minute, and comparisons between wins and losses. The selected role can be configured to focus on a specific position or all roles.

## Tableau Dashboard

Explore the interactive dashboard on Tableau Public:

**[View the League of Legends Performance Dashboard](https://public.tableau.com/app/profile/kevin.lim7109/viz/LeagueofLegendsPerformanceDashboard/Dashboard)**
![League of Legends Performance Dashboard](charts/dashboard.png)

The dashboard visualizes rolling win rate, champion win rate, average KDA, and CS per minute to analyze ranked match performance.

## Features

- **Automated Data Import:** Retrieves ranked match data from the Riot Games API, with retry handling for API rate limits.
- **MySQL Database:** Stores match history and prevents duplicate records using match IDs.
- **Performance Analytics:** Calculates win rates, KDA, CS per minute, gold per minute, and damage per minute.
- **Champion Analysis:** Compares champion performance by games played, win rate, KDA, and CS per minute.
- **Win-Rate Trends:** Visualizes cumulative win rate and a rolling 20-game win rate.
- **Win/Loss Comparison:** Compares gameplay statistics between wins and losses.
- **CSV Reporting:** Exports match history, champion performance, role performance, and win/loss comparison reports.
- **Data Quality Checks:** Checks for missing values and duplicate match IDs.
- **Automated Testing:** Uses pytest to validate analytical functions.
- **Configurable Role Analysis:** Allows analysis of a selected role or all roles through `config.py`.

## Visualizations

The following charts are generated from the local MySQL database. The current configuration focuses on middle lane.

### Ranked Win-Rate Trends

![Ranked win-rate trends](charts/win_rate_trends.png)

The cumulative line tracks performance across all included matches up to each game. The rolling line measures the win rate over the most recent 20 included games.

### Champion Win Rate

![Champion win rate](charts/champion_win_rate.png)

### Champion KDA

![Champion KDA](charts/champion_kda.png)

### Champion CS per Minute

![Champion CS per minute](charts/champion_cs_per_min.png)

## Technologies Used

- Python
- SQL and MySQL
- pandas
- matplotlib
- Riot Games API
- requests
- python-dotenv
- pytest
- Git and GitHub

## Project Structure

| File or folder | Purpose |
|---|---|
| `import_ranked_matches.py` | Retrieves ranked matches and inserts new records into MySQL |
| `analyze_matches.py` | Calculates performance metrics and exports CSV reports |
| `plot_win_rate.py` | Generates cumulative and rolling win-rate trends |
| `plot_champion_stats.py` | Generates champion performance charts |
| `config.py` | Configures the role used for analysis |
| `test_analysis.py` | Tests analytical functions |
| `charts/` | Stores generated PNG visualizations |
| `champion_performance_report.csv` | Champion-level performance metrics |
| `role_performance_report.csv` | Performance metrics by role |
| `ranked_match_history.csv` | Exported ranked match history |
| `win_loss_comparison_report.csv` | Compares statistics between wins and losses |
| `.env` | Local API key and database credentials; excluded from version control |

## Setup and Usage

### 1. Install prerequisites

Install Python, MySQL Server, and Git.

### 2. Install Python dependencies

```bash
pip install requests python-dotenv mysql-connector-python pandas matplotlib pytest
```

### 3. Configure credentials

Create a local `.env` file in the project folder containing your Riot API key and MySQL connection settings. Never commit this file to GitHub.

### 4. Set up the database

Create the `lol_analytics` database and the `matches` table using the schema required by `import_ranked_matches.py`.

### 5. Import ranked matches

```bash
python import_ranked_matches.py
```

The importer targets 100 ranked matches, inserts new records, and leaves existing matches unchanged.

### 6. Configure the analysis role

Edit `config.py` to choose the role to analyze:

```python
SELECTED_ROLE = "MIDDLE"
```

Supported values are `ALL`, `TOP`, `JUNGLE`, `MIDDLE`, `BOTTOM`, and `UTILITY`.

### 7. Run the analysis

```bash
python analyze_matches.py
```

This generates the CSV reports from the available database data.

### 8. Generate the visualizations

```bash
python plot_win_rate.py
python plot_champion_stats.py
```

The scripts save the generated charts in the `charts/` directory.

### 9. Run automated tests

```bash
python -m pytest -v test_analysis.py
```

## Security

API keys and database credentials are stored locally in `.env`, which is excluded from version control through `.gitignore`. Credentials must never be committed to a public repository.

## Future Improvements

- Build an interactive Tableau dashboard for performance trends, champion analysis, and match history.
- Expand analysis to matchup-specific trends.
- Add more analytical tests and reports.
- Explore additional performance metrics and longer-term trends.
