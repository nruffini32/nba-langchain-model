from bs4 import BeautifulSoup
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from constants import teams
from datetime import date

class NBAScraper:
    def __init__(self) -> None:
        self.base_url = "https://www.basketball-reference.com"

        self.links = teams

        options = webdriver.ChromeOptions()
        options.page_load_strategy = "none"
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-images")
        self.driver = webdriver.Chrome(options=options)

        self.season_desc = {}
        self.game_desc = {}

    #####################
    # PRIVATE FUNCTIONS #
    #####################

    # Scrape teams and links from site and return as dictionary
    def _get_links(self):
        response = requests.get(self.base_url + "/teams/")
        soup = BeautifulSoup(response.text, 'html.parser')

        # Create dictionary with team: link
        rows = soup.find(id="teams_active").find_all(class_="full_table")
        dic = {}
        for row in rows:
            tag = row.find("a")
            team = "Trail Blazers" if tag.text.split()[-1] == "Blazers" else tag.text.split()[-1]

            dic[team] = tag.get("href")

        print(dic)

        return dic
    
    # Split dictionary in half so you don't get timed out
    def _split_dict(self, d):
        keys = list(d.keys())
        mid = len(keys) // 2
        
        dict1 = {key: d[key] for key in keys[:mid]}
        dict2 = {key: d[key] for key in keys[mid:]}
        
        return dict1, dict2
    
    def _create_season_desc_dic(self):
        full_url = "https://www.basketball-reference.com/teams/NOP/2024.html"

        self.driver.get(full_url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'team_and_opponent'))
        )
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Getting english descriptions
        header = soup.find("table", id="team_and_opponent").find("thead").find_all("th")
        for tag in header[1:]:
            self.season_desc[tag["data-stat"]] = tag["aria-label"]

    def _create_game_desc_dic(self):
        full_url = "https://www.basketball-reference.com/teams/NOP/2024/gamelog/"

        response = requests.get(full_url)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find("table", id="tgl_basic")

        # Getting english descriptions
        header = table.find("thead").find_all("tr")[1].find_all("th")
        for tag in header:
            stat = tag["data-stat"]
            if stat == "x":
                continue

            if stat == "game_location":
                self.game_desc[stat] = "Game Location"
            else:
                self.game_desc[stat] = tag["aria-label"]


    
    ####################
    # PUBLIC FUNCTIONS #
    ####################


    def get_single_team_season_stats(self, team: str):
        print(f"Fetching season data for {team}..")

        full_url = self.base_url + self.links[team] + "2024.html"

        self.driver.get(full_url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'team_and_opponent'))
        )
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Getting english descriptions if not already created
        if not self.season_desc:
            self._create_season_desc_dic()

        # Getting team statistics   
        rows = soup.find("table", id="team_and_opponent").find("tbody").find_all("tr")
        stats_dic = {}
        games_played = rows[0].find("td", {"data-stat":"g"}).text
        stats_dic["Team"] = team
        stats_dic["Games"] = games_played
        for tag in rows[1].find_all("td")[1:]:
            lookup = tag["data-stat"].replace("_per_g", "")
            stats_dic[self.season_desc[lookup] + " Per Game"] = tag.text

        return stats_dic

    def get_all_team_season_stats(self):
        print("Fetching data for all teams..")
        self._create_season_desc_dic()
        team_data = []

        links1, links2 = self._split_dict(self.links)
        for team in links1:
            dic = self.get_single_team_season_stats(team)
            team_data.append(dic)
        
        print("Sleeping for a min bc www.basketball-reference.com is stupid!")
        time.sleep(61)

        for team in links2:
            dic = self.get_single_team_season_stats(team)
            team_data.append(dic)

        with open('nba_scraper/nba_season_stats.json', 'w') as file:
            json.dump(team_data, file)
        
        print("Done fetching all data\n")
        return team_data
    
    def get_single_team_game_stats(self, team: str, last_n_games: int = 100):
        print(f"Fetching game stats for {team}..")
        full_url = self.base_url + self.links[team] + "2024/gamelog/"

        response = requests.get(full_url)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find("table", id="tgl_basic")

        if not self.game_desc:
            self._create_game_desc_dic()
        
        # Getting statistics
        games = table.find("tbody").find_all("tr")
        lst = []
        for game in games[-last_n_games:]:
            dic = {}
            cols = game.find_all("td")
            for col in cols:
                if col["data-stat"] == "x":
                    continue

                key = self.game_desc[col["data-stat"]]
                if key == "Game Location":
                    val = "Away" if col.text == "@" else "Home"
                    dic[key] = val
                elif key == "W/L":
                    key = "Win/Loss"
                    dic[key] = col.text
                else:
                    dic[key] = col.text

            lst.append(dic)
        
        return lst
    
    # Gets matchups for nba games and betting lines
    def get_matchups(self):
        today = date.today()
        print(f"Fetching matchups for {today}..")

        self.driver.get("https://www.vegasinsider.com/nba/matchups/")
        time.sleep(1)
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        header_rows = soup.find("tbody", id="trends-table-bets--0").find_all("tr", class_="header")
        lst = []
        for header_row in header_rows:
            # Create a new table starting from the header row
            current_table = str(header_row)

            # Find the following siblings (sibling rows) until the next header row
            next_row = header_row.find_next_sibling()
            while next_row and 'header' not in next_row.get('class', []):
                current_table += str(next_row)
                next_row = next_row.find_next_sibling()

            # table for each matchup
            table = BeautifulSoup(current_table, 'html.parser')
            dic = {}

            # Getting matchup and saving as tup
            teams_soup = table.find_all("a", class_="team-name")
            teams = [tag.find("span").text.strip() for tag in teams_soup]
            temp = (teams[0], teams[1])
            tup = tuple(sorted(temp))
            dic["matchup"] = tup

            # Getting abbreviations
            tags = {tag.get("data-abbr"):  tag.find("span").text.strip() for tag in teams_soup}

            # Getting lines
            lines_dic = {}
            lines_soup = table.find("tr", class_="game-odds current")
            spread = lines_soup.find('td', {'data-filter': 'spread'}).text.strip()
            total = lines_soup.find('td', {'data-filter': 'total'}).text.strip()[1:]
            temp = spread.split()[0]
            lines_dic["spread"] = spread.replace(temp, tags[temp])
            lines_dic["total"] = total
            dic["lines"] = lines_dic

            lst.append(dic)

        return lst


    
# nba = NBAScraper()
# nba.get_single_team_season_stats("Nets")
# data = nba.get_all_team_season_stats()
# for team in ["Pistons", "Pelicans"]:
#     nba.get_single_team_game_stats(team)
# nba.get_matchups()


    
    
    
    