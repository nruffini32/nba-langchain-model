import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd
import sqlite3
from dotenv import load_dotenv
import os


class Email:
    def __init__(self) -> None:
        load_dotenv()
        self.username = os.environ.get("EMAIL")
        self.password = os.environ.get("EMAIL_PASS")
        self.smtp_server = 'smtp.gmail.com'
        self.smtp_port = 587
        self.root_path = os.environ.get("ROOT_PATH")

        self.to_emails = [] ### ADD EMAIL HERE

        self.server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        self.server.starttls()
        self.server.login(self.username, self.password)


    def gen_result_message(self, outcome_file):

        df = pd.read_csv(outcome_file)
        sWin = (df["result"] == "W").sum()
        sLose = (df["result"] == "L").sum()
        sPush = (df["result"] == "Push").sum()

        ouWin = (df["ouresults"] == "W").sum()
        ouLose = (df["ouresults"] == "L").sum()
        ouPush = (df["ouresults"] == "Push").sum()

        ##### NEEED TO DEFINE THESE VARIABLES ABOVE
        conn = sqlite3.connect(f'{self.root_path}/NBA_model_results.db')
        cur = conn.cursor()


        # TOTAL RESULTS
        cur.execute("select sum(win) from spread_results")
        sWinTotal = cur.fetchone()[0]
        cur.execute("select sum(lose) from spread_results")
        sLoseTotal = cur.fetchone()[0]
        cur.execute("select sum(push) from spread_results")
        sPushTotal = cur.fetchone()[0]

        cur.execute("select sum(win) from ou_results")
        ouWinTotal = cur.fetchone()[0]
        cur.execute("select sum(lose) from ou_results")
        ouLoseTotal = cur.fetchone()[0]
        cur.execute("select sum(push) from ou_results")
        ouPushTotal = cur.fetchone()[0]

        message = f"""
            <b>Yesterday's Results</b>
            <br>ATS: {sWin}-{sLose}-{sPush}
            <br>O/U: {ouWin}-{ouLose}-{ouPush}
            <br>
            <br>
            <b>Total Model Results</b>
            <br>ATS: {sWinTotal}-{sLoseTotal}-{sPushTotal}
            <br>O/U: {ouWinTotal}-{ouLoseTotal}-{ouPushTotal}
            <br><br><b>**Oracle results are given because lines may change**</b>
            <br><br><h1>Today's Picks</h1>
        """

        return message
        

    def gen_message(self, file, outcome_file):
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file)

        result_message = self.gen_result_message(outcome_file)

        message_text = result_message
        # Iterate through the rows and format each row
        for index, row in df.iterrows():
            oracle_team = row['model_prediction'].split("-")[0].strip()
            oracle_num = row['model_prediction'].split("-")[-1].strip()
            matchup = f"{row['team1']} vs {row['team2']} | Oracle has {oracle_team} by {oracle_num} and total of {row['predicted_score1']+row['predicted_score2']}"
            pick = f"Spread: {row['pick']} | {row['value']} points of value"
            oupick = f"O/U: {row['oupick']} | {row['ouvalue']} points of value"
            
            formatted_row = f"<b>{matchup}</b><br>{pick}<br>{oupick}"
            
            # Print or use the formatted row as needed
            message_text += (f"{formatted_row}<br><br>")
        
        return message_text


    def send_email(self, subject, message):
        for email in self.to_emails:
            print(f"Sending email to {email}")
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = email
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'html'))

            # Send the email
            self.server.sendmail(self.username, email, msg.as_string())

        
        self.server.quit()

    
