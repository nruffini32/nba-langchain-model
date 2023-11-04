import os
from dotenv import load_dotenv
import pandas as pd
from datetime import date
import sqlite3

class Vegas:
    def __init__(self) -> None:
        load_dotenv()
        self.root_path = os.environ.get("ROOT_PATH")

    def check_picks(self, scores):
        print("Checking picks from yesterday..")
        # Getting most recent predictions
        folder_path = self.root_path + "/predictions"
        files = os.listdir(folder_path)
        sorted_files = sorted(files, key=lambda x: os.path.getctime(os.path.join(folder_path, x)), reverse=True)
        file = folder_path + "/" + sorted_files[0]

        df = pd.read_csv(file)
        results = []
        ouresults = []
        for index, row in df.iterrows():
            team1 = row["team1"]
            team2 = row["team2"]
            key = (team1, team2)

            # Get the actual scores from the 'scores' dictionary
            game_result = scores[key]
            actual_score1 = game_result[team1]
            actual_score2 = game_result[team2]

            # OU pick logic
            actual_total = actual_score1 + actual_score2
            total = row["total"]

            if row["oupick"] == "No Pick":
                ouresults.append("No Pick")
            elif actual_total == total:
                ouresults.append("Push")
            elif row["oupick"] == "Over":
                if actual_total < total:
                    ouresults.append("L")
                else:
                    ouresults.append("W")
            elif row["oupick"] == "Under":
                if actual_total < total:
                    ouresults.append("W")
                else:
                    ouresults.append("L")

            # Before doing stuff with pick, check if we didn't have a pick
            pick = row['pick']
            if pick == "No Pick":
                results.append("No Pick")
                continue

            # ADD FIX PICK EM LOGIC AT SOME POINT ----

            # Extract team and spread from pick column
            picked_team = pick.rsplit(' ', 1)[0]
            other_team = team2 if team1 == picked_team else team1
            spread = float(pick.rsplit(' ', 1)[-1])

            game_result[picked_team] += spread

            # pick logic
            if game_result[picked_team] > game_result[other_team]:
                results.append("W")
            elif game_result[picked_team] < game_result[other_team]:
                results.append("L")
            else:
                results.append("Push")

        

        df['result'] = results
        df["ouresults"] = ouresults
        
        prediction_date = file.split("_")[-1]

        outcome_file = self.root_path + f"/outcomes/outcome_{prediction_date}"
        df[["team1", "team2", "result", "ouresults", "value" ,"ouvalue"]].to_csv(outcome_file, index=False)

        print(f"Done! Stored at {outcome_file}\n")
        return outcome_file


    def store_results(self, outcome_file):
        db = "NBA_model_results.db"
        print("Storing results in NBA_model_results.db..")
        df = pd.read_csv(outcome_file)
        prediction_date = outcome_file.split("_")[-1].replace(".csv", "")

        sWin = (df["result"] == "W").sum()
        sLose = (df["result"] == "L").sum()
        sPush = (df["result"] == "Push").sum()

        ouWin = (df["ouresults"] == "W").sum()
        ouLose = (df["ouresults"] == "L").sum()
        ouPush = (df["ouresults"] == "Push").sum()

        conn = sqlite3.connect(f'{self.root_path}/{db}')
        cur = conn.cursor()

        cur.execute(f"INSERT INTO spread_results VALUES ('{prediction_date}', {sWin}, {sLose}, {sPush})")
        cur.execute(f"INSERT INTO ou_results VALUES ('{prediction_date}', {ouWin}, {ouLose}, {ouPush})")

        conn.commit()

        cur.close()
        conn.close()
        print("Done storing results!\n")


    def check_and_store_results(self, scores):
        outcome_file = self.check_picks(scores)
        self.store_results(outcome_file)
        return outcome_file




# v = Vegas()
# v.check_picks()
# v.store_results("")
# v.check_and_store_results()