from bs4 import BeautifulSoup
import requests
import sqlite3


# Scraping teams from pro-basketball-reference and storing in database as teams
def main():
    print("Creating teams table in database...")
    # Scrape teams from site and create database
    response = requests.get("https://www.basketball-reference.com/teams/")
    soup = BeautifulSoup(response.text, 'html.parser')

    # Create dictionary with team: link
    rows = soup.find(id="teams_active").find_all(class_="full_table")
    dic = {}
    for row in rows:
        tag = row.find("a")
        team = "Trail Blazers" if tag.text.split()[-1] == "Blazers" else tag.text.split()[-1]

        dic[team] = tag.get("href")
    
    conn = sqlite3.connect('nba.db')
    cur = conn.cursor()
    
    cur.execute("DROP TABLE IF EXISTS teams")
    conn.commit()
    sql = """
        CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team TEXT,
        link TEXT
        )
    """
    cur.execute(sql)
    conn.commit()

    for team, link in dic.items():
        cur.execute('INSERT INTO teams (team, link) VALUES (?, ?)', (team, link))
    
    conn.commit()
    
    cur.close()
    conn.close()

    print("Done!")
    print()


if __name__ == "__main__":
    main()