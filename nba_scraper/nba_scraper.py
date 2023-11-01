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
    
    # Gets matchups for nba games and store in DB "1 2", "20 22"
    # ADDD LINES TO THIS ???
    def get_matchups(self):
        today = date.today()
        print(f"Fetching matchups for {today}..")

        response = requests.get("https://www.vegasinsider.com/nba/matchups/")
        soup = BeautifulSoup(response.text, 'html.parser')
        games = soup.find_all("a", class_="team-name")
        num_matchups = len(games) // 2
        num_matchups = num_matchups // 2

        # Getting matchups and storing in matchups
        matchups = []
        for i in range(num_matchups):
            i = i*2
            team1 = games[i].find("span").text.strip()
            team2 = games[i+1].find("span").text.strip()
            tup = (team1, team2)
            matchups.append(tup)
        
        print("Matchups:", matchups)
        print()
        return matchups


    
nba = NBAScraper()
# nba.get_single_team_season_stats("Nets")
# data = nba.get_all_team_season_stats()
# for team in ["Pistons", "Pelicans"]:
#     nba.get_single_team_game_stats(team)
# nba.get_matchups()


    
    
    
    