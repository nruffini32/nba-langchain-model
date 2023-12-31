# nba-langchain-model

## About
This project is an NBA sports betting model using LangChain.
The running of main.py triggers the below steps:
1. Fetches yesterdays scores
2. Checks yesterdays picks and stores results in a sqlite3 database
3. Make picks for today
4. Send email with results and picks

## Getting Started
1. Install below dependencies
  * <a href="https://www.crummy.com/software/BeautifulSoup/bs4/doc/">***bs4***</a>
  * <a href="https://www.selenium.dev/documentation/">***Selenium***</a>
  * <a href="https://python.langchain.com/docs/get_started/introduction">***LangChain***</a>
  * <a href="https://pandas.pydata.org/docs/">***Pandas***</a>
2. Create .env file and configure below variables
```
    EMAIL=example@gmail.com
    EMAIL_PASS=password
    ROOT_PATH=/root/file/path
    OPENAI_API_KEY=123232youropen_api_key
```
3. Update `self.to_emails` variable in email_class.py with emails you want to send to
4. Run `Model().run()` by itself the first day.
  
## Usage
Run main.py before the NBA games start for the day. 
If <a href="https://www.vegasinsider.com/nba/matchups/">vegasinsider</a> or <a href="https://www.basketball-reference.com/">basketball-reference</a> ever change the structure of their html the script will break.

***-----DISCLAIMER This model does not provide any edge on sports books. This was made for educational purposes only.-----***


