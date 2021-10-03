import requests
from bs4 import BeautifulSoup
import re
import os
import pandas as pd


def get_useful_columns(result):
    """
    Filter csv columns to make use of:
    GD - goal difference, FTHG (Full time home goals), HST (Home shots on target)
    B365H (Odds favouring home team in the match by Bet365),
    B365D - draw, B365A - away, FTR (full time result)
    """
    result["GD"] = result["FTHG"] - result["FTAG"]

    return result[["Date", "HomeTeam", "AwayTeam",
                   "FTHG", "FTAG", "GD",
                   "HST", "AST",
                   "B365H", "B365D", "B365A", "FTR"
                   ]]


def get_csv_files(from_year, to_year):
    """
    Uses the webpage football-data.co.uk to obtain historic data (even games played recently),
    utitlizes BeatifulSoup to get to the csv files of the leagues desired
    - csv files are stored locally
    """
    base_url = "http://www.football-data.co.uk/"
    competition_urls = {
        base_url + "englandm.php": "E0",
        base_url + "spainm.php": "SP1",
        base_url + "germanym.php": "D1",
        base_url + "italym.php": "I1",
        base_url + "francem.php": "F1"
    }
    new_directory = "historic"
    for url, competition in competition_urls.items():
        request = requests.get(url)
        soup = BeautifulSoup(request.content, features="html.parser")
        allsearch = ""
        complete_urls = []
        # reading all the links on the selected page.
        for link in soup.find_all('a'):
            mysearch = link.get('href')
            allsearch = allsearch + ' ' + mysearch
        array = allsearch.split()
        season_files = [
            file for file in array
            if re.search(
                "^mmz.*.{}.csv$".format(competition), str(file)
            )
        ]
        for file in (season_files):
            url = base_url + str(file)
            complete_urls.append(url)

        to_year -= from_year
        from_year = 0
        chosen_urls = complete_urls[from_year: to_year]
        readings = pd.DataFrame()
        for url in chosen_urls:
            reader = pd.read_csv(url, sep=',', header=0, error_bad_lines=False)
            readings = readings.append(reader)
        if not os.path.exists(new_directory):
            os.mkdir(new_directory)
        readings = get_useful_columns(readings)
        filename = new_directory + "/" + competition + ".csv"
        readings.to_csv(filename, index=False)

if __name__ == "__main__":
    get_csv_files(2010, 2022)
