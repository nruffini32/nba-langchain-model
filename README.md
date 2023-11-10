# nba-langchain-model

## About
Thi project is an NBA sports betting model using LangChain.
The running of main.py triggers the below steps:
1. Fetches yesterdays scores
2. Checks yesterdays picks and stores results in a splite3 database
3. Make picks for today
4. Send email with results and picks

## Getting Started
1. Install below dependencies with the requirements.txt file: `pip install -r requirements.txt`
  * <a href="https://www.crummy.com/software/BeautifulSoup/bs4/doc/">***bs4***</a>
  * <a href="https://www.selenium.dev/documentation/">***selenium***</a>

create .env
- EMAIL, EMAIL_PASS, ROOT_PATH, OPENAI_API_KEY

update emails - set up for gmail rn - will have to create app password

Run model alone for the first time
