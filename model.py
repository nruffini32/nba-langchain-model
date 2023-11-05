from nba_scraper import NBAScraper
import time
import json
from langchain.llms import OpenAI
from dotenv import load_dotenv
import os
from langchain.schema.messages import HumanMessage, SystemMessage
import csv
import shutil
import re
from datetime import date
from email_class import Email
import pandas as pd


class Data:
    def __init__(self) -> None:
        self.nba = NBAScraper()
        self.season_stats_dic =  self.nba.get_all_team_season_stats()
        self.matchups_dic = self.nba.get_matchups()
        self.team_games_dic = self._create_games_stats_dic()

    def _create_games_stats_dic(self):
        print("Creating dic for all teams game stats Zzzz...")
        time.sleep(61)

        # Creating big dic
        teams1, teams2 = self.nba._split_dict(self.nba.links)
        dic = {}
        for team in teams1:
            dic[team] = self.nba.get_single_team_game_stats(team, 3)
        print("SLEEP zzz")
        time.sleep(61)
        for team in teams2:
            dic[team] = self.nba.get_single_team_game_stats(team, 3)

        print("Done creating games stats dic!\n")

        return dic


class Model:
    def __init__(self) -> None:
        load_dotenv()
        self.root_path = os.environ.get("ROOT_PATH")
        self.d = Data()


    #####################
    # PRIVATE FUNCTIONS #
    #####################
    
    def _format_dictionary(self, dic):
        formatted_string = ""
        for key, value in dic.items():
            formatted_string += f"{key}: {value}\n"

        # Remove the trailing newline character at the end
        formatted_string = formatted_string.strip()

        return formatted_string
    
    def _format_lst_dic(self, lst):
        formatted_strings = []
        for data_dict in lst:
            formatted_string = "-- NEW GAME --\n"
            for key, value in data_dict.items():
                formatted_string += f"{key}: {value}\n"
            # Remove the trailing newline character at the end
            formatted_string = formatted_string.strip()
            formatted_strings.append(formatted_string)

        # Join the formatted strings with a newline to create the final result
        result = "\n\n".join(formatted_strings)

        return result

    #####################
    # PUBLIC FUNCTIONS #
    #####################

    def make_prediction(self, team1, team2):
        print(f"Making prediction for {team1} and {team2}")

        ################

        teamData1 = self._format_dictionary(self.d.season_stats_dic[team1])
        indvGameData1 = self._format_lst_dic(self.d.team_games_dic[team1])

        teamData2 = self._format_dictionary(self.d.season_stats_dic[team2])
        indvGameData2 = self._format_lst_dic(self.d.team_games_dic[team2])


        # Prompts -- weird formatting is needed look at prompts folder
        system_template = """You are an AI Machine Learning model who predicts NBA scores.
You are given data for two teams.
For each team you are given their total season statistics and their statistics for their last 3 games.
Use this data and any other resources available to you to act as an AI Machine 
Learning Model to predict the score between the two teams.\n"""

        human_input = f"""\nPredict the score between the two teams using the data below.
Give the prediction in the following format
Predicted Score: [team1]: [score], [team2]: [score]
Teams: {team1} and {team2}

--- {team1} FULL SEASON DATA BELOW ---
{teamData1}\n
--- {team1} LAST 3 GAMES DATA BELOW ---
{indvGameData1}\n\n
--- {team2} FULL SEASON DATA BELOW ---
{teamData2}\n
--- {team2} LAST 3 GAMES DATA BELOW ---
{indvGameData2}\n

"""

        messages = [
            SystemMessage(content=system_template),
            HumanMessage(content=human_input),
        ]

        chat = OpenAI(temperature=0.6)
        output = chat.invoke(messages).strip()
        print(output)

        return output
    
    def store_prediction(self, team1, team2, spread, total, prediction_string, csv_writer):

        temp = prediction_string.replace("Predicted Score: ", "")
        prediction = {i.split(":")[0].strip(): float(i.split(":")[1].strip()) for i in temp.split(",")}
        score1 = prediction[team1]
        score2 = prediction[team2]

        if score1 > score2:
            model_prediction =f"{team1} -{score1-score2}"
        elif score1 < score2:
            model_prediction =f"{team2} -{score2-score1}"
        else:
            model_prediction =f"Even"

        # pick logic ---- NEED TO ADD PICK EM LOGIC STILL
        favored_team = spread.split("-")[0].strip()
        by_points = float(spread.split("-")[-1])
        prediction[favored_team] -= by_points
        print(prediction)

        other_team = team2 if team1 == favored_team else team1
        print(favored_team, other_team, by_points)

        if prediction[favored_team] > prediction[other_team]:
            pick = spread
            value = prediction[favored_team] - prediction[other_team]
        elif prediction[favored_team] < prediction[other_team]:
            pick = f"{other_team} +{by_points}"
            value = prediction[other_team] - prediction[favored_team]
        else:
            pick = "No Pick"
            value = "No Pick"

        # ou pick logic
        predicted_total = score1 + score2
        if predicted_total > total:
            oupick = "Over"
            ouvalue = predicted_total - total
        elif predicted_total < total:
            oupick = "Under"
            ouvalue = total - predicted_total
            pass
        else:
            oupick = "No Pick"
            ouvalue = "No Pick" 

        csv_writer.writerow([team1, team2, score1, score2, model_prediction, total, pick, value, oupick, ouvalue])
        print([team1, team2, score1, score2, model_prediction, pick, value, oupick, ouvalue])

    


    # Predicted Score: Pistons: 112, Pelicans: 108
    def run(self):
        print("Running full model")

        # Clear prompts folder
        prompts_folder_path = f"{self.root_path}/prompts"
        if os.path.exists(prompts_folder_path):
            shutil.rmtree(prompts_folder_path)
        os.makedirs(prompts_folder_path)

        file_name = f"{self.root_path}/predictions/predictions_{date.today()}.csv"
        csv_file = open(file_name, 'w', newline='')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["team1", "team2", "predicted_score1", "predicted_score2", "model_prediction", "total", "pick", "value", "oupick", "ouvalue"])

        for matchup in self.d.matchups_dic:
            team1 = matchup["matchup"][0]
            team2 = matchup["matchup"][1]
            spread = matchup["lines"]["spread"]
            total = float(matchup["lines"]["total"])

            prediction_string = self.make_prediction(team1, team2)
            print("INPUTS:", team1, team2, spread, total, prediction_string)
            self.store_prediction(team1, team2, spread, total, prediction_string, csv_writer)
            print()

        print("Done running model!\n")

        return file_name
    

# m = Model()
# m.run()


