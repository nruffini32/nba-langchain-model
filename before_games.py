from before_games_files.nba import NBA
from before_games_files.model import Model
from dotenv import load_dotenv


def main():

    load_dotenv()

    # 1. Make sure database exists (setup.py)

    # 2. Get matchups for the day and update statistics in database
    nba = NBA()
    matchups = nba.get_and_store_matchups()
    nba.update_statistics()

    # 3. Run model for matchups
    m = Model()
    matchups = []
    # for matchup in matchups:

    #     m.run(team1, team2)



    return

if __name__ == "__main__":
    main()