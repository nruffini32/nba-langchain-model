import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import sqlite3

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
        self.cur.execute("SELECT link FROM teams")
        rows = self.cur.fetchall()
        return [r[0] for r in rows]


    # # Get full season data and store in DB
    def _get_full_season_data(self):
        print("Fetching season team data and uploading to database...")

        response = requests.get("https://www.vegasinsider.com/nba/matchups/")
        soup = BeautifulSoup(response.text, 'html.parser')
        games = soup.find_all("a", class_="team-name")

        print("Done!\n")
        return
    
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

NBA()._get_links()
    
    
    
    