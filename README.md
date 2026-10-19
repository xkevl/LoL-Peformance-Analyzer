\# League of Legends Performance Analyzer



A Python and SQL analytics project that analyzes ranked League of Legends match history using the Riot Games API and MySQL.



\## Project Overview



This project imports ranked solo/duo match data, stores it in a MySQL database, and analyzes gameplay performance using Python. It generates reports and visualizations to identify trends in win rate, champion performance, and differences between wins and losses.



\## Features



\- \*\*Automated Data Import:\*\* Retrieves ranked match data through the Riot Games API.

\- \*\*MySQL Database:\*\* Stores match history and prevents duplicate records during repeated imports.

\- \*\*Performance Analytics:\*\* Calculates win rate, KDA, CS per minute, gold per minute, and damage per minute.

\- \*\*Champion Analysis:\*\* Compares champion performance using games played, win rate, and other performance metrics.

\- \*\*Trend Visualization:\*\* Plots cumulative and rolling 10-game win rates.

\- \*\*Win/Loss Comparison:\*\* Compares performance statistics between wins and losses.

\- \*\*Data Quality Checks:\*\* Checks for missing values and duplicate match IDs.

\- \*\*Automated Testing:\*\* Uses pytest to validate analytical functions.



\## Technologies Used



\- Python

\- SQL and MySQL

\- pandas

\- matplotlib

\- Riot Games API

\- pytest

\- Git and GitHub



\## Project Structure



| File | Purpose |

|---|---|

| `import\_ranked\_matches.py` | Imports ranked match data into MySQL |

| `analyze\_matches.py` | Calculates performance metrics and exports reports |

| `plot\_win\_rate.py` | Visualizes win-rate trends |

| `plot\_champion\_stats.py` | Visualizes champion performance |

| `config.py` | Configures the role used for analysis |

| `test\_analysis.py` | Tests analytical functions |



\## Setup



1\. Install Python and MySQL.

2\. Install the required Python packages:



&#x20;  ```bash

&#x20;  pip install requests python-dotenv mysql-connector-python pandas matplotlib pytest

&#x20;  ```



3\. Create a local `.env` file containing your Riot API key and MySQL connection settings. Never upload this file to GitHub.

4\. Create the `lol\_analytics` database and the `matches` table expected by the import script.

5\. Run the importer:



&#x20;  ```bash

&#x20;  python import\_ranked\_matches.py

&#x20;  ```



6\. Run the analysis:



&#x20;  ```bash

&#x20;  python analyze\_matches.py

&#x20;  ```



7\. Generate the charts:



&#x20;  ```bash

&#x20;  python plot\_win\_rate.py

&#x20;  python plot\_champion\_stats.py

&#x20;  ```



8\. Run the tests:



&#x20;  ```bash

&#x20;  python -m pytest -v test\_analysis.py

&#x20;  ```



\## Security



API keys and database credentials are stored locally in `.env`, which is excluded from version control.



\## Future Improvements



\- Expand analysis across multiple accounts.

\- Explore matchup-specific trends.

\- Add more analytical tests and reports.

\- Develop an interactive performance dashboard.



