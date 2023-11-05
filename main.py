from nba_scraper import NBAScraper
from model import Model
from vegas import Vegas
from email_class import Email

## Going to need to fix pick em lines at some point
def main():
    nba = NBAScraper()

    # Get scores of yesterday
    scores = nba.get_yesterday_scores()
    
    # Check picks and store in outcomes/DB
    v = Vegas()
    outcome_file = v.check_and_store_results(scores)

    # Make picks for today
    m = Model()
    prediction_file = m.run()

    # Send email with picks
    print("Sending emails")
    e = Email()
    message = e.gen_message(prediction_file, outcome_file)
    e.send_email("NBA Picks for Today", message)

if __name__ == "__main__":
    main()
