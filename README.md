# VLR.gg Stats Scraper

This is a web scraping tool built in Python using Streamlit to pull and analyze detailed match statistics from VLR.gg. The application is designed to help analysts, coaches, and Valorant fans access comprehensive match data for research and study.

### Features

The scraper provides three main levels of data analysis to give you a complete picture of a team's performance.

1. **Overall Team History Stats:** Scrape a team's full match history to get general win/loss records, event participation, and overall performance trends.

2. **Head-to-Head History Stats:** Analyze specific matchups between two teams to see their historical win/loss record against each other, including scores from past games.

3. **Map History Stats:** Dive deep into specific matches to get detailed, map-by-map statistics, including player stats, round-by-round results, and pick/ban data.

### Installation

To run this application, you will need to set up the project environment using one of the following methods.

1. **Using `uv`:**

   If you are using `uv`, you can install the dependencies from the `pyproject.toml` and `uv.lock` files.

   ```bash
   uv sync
   
   ```

2. **Using `nix flake`:**

   If you have Nix installed, you can use the `nix develop` command to enter a development shell with all dependencies ready to go.

   ```bash
   nix develop
   
   ```

### Usage

To start the Streamlit application, run the following command in your terminal:

```bash
streamlit run your_main_app_file.py

```

This will launch a local web server, and a new tab will open in your browser where you can interact with the app.

Or in another case, you want to use the scraping functionality, you could just import and then play around with

```python
from scraper import Scraper

Scraper.get_match_history(<arguments>)
```

