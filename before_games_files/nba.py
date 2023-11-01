import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup, Comment
import requests
import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import html
from lxml import etree
from selenium.webdriver.chrome.options import Options

from requests_html import HTMLSession

load_dotenv()

class NBA:
    def __init__(self) -> None:
        self.root_path = os.getenv("ROOT_PATH")
        self.conn = sqlite3.connect(self.root_path + "/nba.db")
        self.cur = self.conn.cursor()

    # Gets matchups for nba games and store in DB "1 2", "20 22"
    def get_and_store_matchups(self):
        print("Fetching matchups and storing in database...")
        # Creating matchups table if doesn't exists
        self.cur.execute("DROP TABLE IF EXISTS matchups")
        self.conn.commit()
        sql = """
            CREATE TABLE matchups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team1 INTEGER,
            team2 INTEGER
            )
        """
        self.cur.execute(sql)
        self.conn.commit()

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

            self.cur.execute(f'INSERT INTO matchups (team1, team2) VALUES (?, ?)', (team1, team2))
        
        self.conn.commit()
        
        print("Matchups:", matchups)
        print()
        return matchups
    
    def _get_links(self):
        self.cur.execute("SELECT * FROM teams")
        rows = self.cur.fetchall()
        return {r[1]: r[2] for r in rows}
    
    # Split dictionary in half so you don't get timed out
    def _split_dict(self, d):
        keys = list(d.keys())
        mid = len(keys) // 2
        
        dict1 = {key: d[key] for key in keys[:mid]}
        dict2 = {key: d[key] for key in keys[mid:]}
        
        return dict1, dict2


    # # Get full season data and store in DB
    def _get_full_season_data(self):
        print("Fetching season team data and uploading to database...")

        base_url = "https://www.basketball-reference.com"
        links = self._get_links()
        first_half, second_half = self._split_dict(links)

        # Configuring selenium webdriver for dynamically loaded content
        options = webdriver.ChromeOptions()
        options.page_load_strategy = "none"
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-images")
        driver = webdriver.Chrome(options=options)

        # Getting statistics for each team
        for team in first_half:

            #
            full_url = base_url + first_half[team] + "2024.html"
            driver.get(full_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'team_and_opponent'))
            )
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, "html.parser")      
            tables = soup.find(id="team_and_opponent")


            break

        driver.quit()
        return

        time.sleep(60)

        for team in second_half:
            continue


        print("Done!\n")
    
    # Gets the last X game data for team and stores in DB
    def _get_individual_game_data(self, team):
        return
    
    # Updates the database with full season data and 
    def update_statistics(self):
        self._get_full_season_data()
        self._get_individual_game_data()

    def __del__(self):
        self.cur.close()
        self.conn.close()

NBA()._get_full_season_data()
    
    
    
    