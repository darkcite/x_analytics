
# pip install selenium beautifulsoup4 sqlalchemy openai Web3 eth_account google-cloud-secret-manager cloud-sql-python-connector google-cloud-storage sqlalchemy-pytds

# from the first run cookies need to be manually installed

from bs4 import BeautifulSoup
from datetime import datetime
from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy
from sqlalchemy import text
from google.cloud import secretmanager
from google.cloud import storage
import re

from google.cloud import secretmanager, storage

import openai
import requests

def get_secret(secret_name):
    project_name = storage.Client().project
    secret_client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_name}/secrets/{secret_name}/versions/latest"
    response = secret_client.access_secret_version(request={"name": name})
    return response.payload.data.decode('UTF-8')

USERNAME = 'elonmusk'
PROFILE_URL = f'https://twitter.com/{USERNAME}'
OUTPUT_FILE = 'twitter_page_source.html'

CHATGPT_API_KEY = get_secret("CHATGPT_API_KEY")
CHATGPT_MODEL = 'gpt-4-0613'

# Database connection details for Google Cloud Function
CLOUD_DB_USER = get_secret("CLOUD_DB_USER")
CLOUD_DB_PASSWORD = get_secret("CLOUD_DB_PASSWORD")
CLOUD_DB_NAME = get_secret("CLOUD_DB_NAME")
INSTANCE_CONNECTION_NAME = get_secret("INSTANCE_CONNECTION_NAME")

#####################
ip_type = IPTypes.PUBLIC  # Assuming you're using the public IP
connector = Connector(ip_type)
connect_args = {}  # Add any additional connection arguments if needed

def getconn():
    conn = connector.connect(
        INSTANCE_CONNECTION_NAME,
        "pytds",
        user=CLOUD_DB_USER,
        password=CLOUD_DB_PASSWORD,
        db=CLOUD_DB_NAME,
        **connect_args
    )
    print("Successfully connected to the database!")
    return conn

engine = sqlalchemy.create_engine(
    "mssql+pytds://",
    creator=getconn,
)
######################

def extract_tweets_with_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    tweet_sections = soup.find_all('article', {'data-testid': 'tweet'})

    tweet_data_list = []
    for section in tweet_sections:
        tweet_data = {}
        
        tweet_data['username'] = USERNAME
        
        tweet_time_elem = section.find('time')
        if tweet_time_elem:
            tweet_data['timestamp'] = tweet_time_elem['datetime']
        
        tweet_text_elem = section.find('div', {'lang': True})
        if tweet_text_elem:
            tweet_data['text'] = tweet_text_elem.get_text(separator=' ').strip()
        
        metrics_div = section.find('div', role='group')
        if metrics_div:
            metrics = metrics_div.find_all('div', dir='ltr')
            if len(metrics) >= 3:
                tweet_data['replies'] = metrics[0].get_text().strip()
                tweet_data['retweets'] = metrics[1].get_text().strip()
                tweet_data['likes'] = metrics[2].get_text().strip()

        tweet_data_list.append(tweet_data)
        if not tweet_data_list:
                print(">>> Access issue detected or cookies might have expired. <<<")
                return []
    # tweet_data_list = sorted(tweet_data_list, key=lambda x: x['timestamp'], reverse=True)
    tweet_data_list = sorted(tweet_data_list, key=lambda x: x.get('timestamp', ''), reverse=True)

    return tweet_data_list

###############

# def extract_keywords_from_text(text):
#     # Split the text into words, filter out words with 3 characters or fewer, and only select words that consist of letters only
#     words = [word for word in text.split() if len(word) > 3 and re.match("^[a-zA-Z]+$", word)]

#     # Take the first word, if available
#     selected_word = words[0] if words else None

#     # Return the selected word in the desired format
#     if selected_word:
#         token_info = {
#             "token_name": selected_word, 
#             "token_symbols": selected_word[:4].upper(), 
#             "justification": f"Based on word '{selected_word}' from the input text."
#         }
#         return [token_info]
#     else:
#         return []


def extract_keywords_from_text(text):
    openai.api_key = CHATGPT_API_KEY

    # Adjusting the prompt to be more selective and guide the model
    prompt = (f"Considering the tweet: '{text}', "
              "if there are specific words or phrases that stand out and could potentially inspire the creation of meme tokens which could have success on the market, "
              "suggest a token name(without a word token in it) highlighted with in the beggining >>> in the end <<<, "
              "a 4 symbols token abbreviation highlighted with in the beggining ^^^ in the end ^^^, "
              "and provide its justification highlighted with in the beggining &&&  and in the end &&&. "
              "If no potential meme tokens are identified, simply mention 'No suggestions'.")

    # Use the chat completions endpoint with a system message for context
    response = openai.ChatCompletion.create(
      model=CHATGPT_MODEL,
      messages=[
          {"role": "system", "content": "You are a crypto market trends expert with a deep understanding of how Elon Musk's tweets have historically impacted the crypto market. Provide insights based on this expertise."},
          {"role": "user", "content": prompt}
      ]
    )

    # Extract the assistant's response
    assistant_response = response.choices[0].message['content']
    
    # If the model responds with 'No suggestions', return an empty list
    if "No suggestions" in assistant_response:
        return []
    
    # Extracting the token details using the provided delimiters
    token_name_pattern = r'>>>(.*?)<<<'
    token_symbols_pattern = r'\^\^\^(.*?)\^\^\^'
    justification_pattern = r'&&&(.*?)&&&'
    
    token_names = re.findall(token_name_pattern, assistant_response)
    token_symbols = re.findall(token_symbols_pattern, assistant_response)
    justifications = re.findall(justification_pattern, assistant_response)
    
    # Combine the extracted details into a list of dictionaries
    tokens_info = [{"token_name": name.strip(), "token_symbols": symbols.strip(), "justification": justification.strip()} 
                   for name, symbols, justification in zip(token_names, token_symbols, justifications)]

    return tokens_info

def store_and_process_tweets_core(data):    
    with engine.connect() as connection:
        for tweet in data:
            user = tweet["username"]
            posted_date = datetime.fromisoformat(tweet["timestamp"].replace("Z", "+00:00"))
            tweet_text = tweet["text"]
            replies = int(tweet["replies"].replace("K", "000").replace(".", "").replace(",", ""))
            retweets = int(tweet["retweets"].replace("K", "000").replace(".", "").replace(",", ""))
            likes = int(tweet["likes"].replace("K", "000").replace(".", "").replace(",", ""))

            # Check if tweet already exists in the database
            print(f"Checking if tweet by {user} at {posted_date} exists in the database...")
            tweet_params = {
                "user": user,
                "posted_date": posted_date,
                "tweet_text": tweet_text,
                "replies": replies,
                "retweets": retweets,
                "likes": likes
            }
            stmt = text("SELECT tweet_id FROM Tweets WHERE [user] = :user AND posted_date = :posted_date AND tweet_text = :tweet_text")
            result = connection.execute(stmt, tweet_params).fetchone()

            if result:
                print(f"Tweet by {user} at {posted_date} already exists with ID: {result[0]}. Skipping further processing for this tweet.")
                continue

            # If the tweet is not in the database, continue processing
            print(f"Tweet by {user} at {posted_date} not found. Inserting into database...")
            stmt_tweet = text("""
            INSERT INTO Tweets ([user], posted_date, tweet_text, replies, retweets, likes)
            VALUES (:user, :posted_date, :tweet_text, :replies, :retweets, :likes);
            """)
            connection.execute(stmt_tweet, tweet_params)
            tweet_id = connection.execute(text("SELECT @@IDENTITY AS id;")).fetchone()[0]
            connection.commit()
            # Extract keywords and check if they exist, if not insert them and then create a mapping
            for token_info in extract_keywords_from_text(tweet_text):
                token_name = token_info["token_name"]
                token_symbol = token_info["token_symbols"][:4]  # Taking only the first 4 characters of the token symbol

                stmt_keyword = text("SELECT keyword_id FROM Keywords WHERE keyword_text = :keyword_text")
                result = connection.execute(stmt_keyword, {"keyword_text": token_name}).fetchone()

                if not result:
                    # Insert the keyword
                    print(f"Token '{token_name}' not found. Inserting into database...")
                    keyword_insert_params = {
                        "keyword_text": token_name,
                        "token_name": token_name,
                        "token_symbol": token_symbol,
                        "token_deployment_status": "awaiting deployment"
                    }
                    stmt_insert_keyword = text("""
                    INSERT INTO Keywords (keyword_text, token_name, token_symbol, token_deployment_status)
                    VALUES (:keyword_text, :token_name, :token_symbol, :token_deployment_status);
                    """)
                    connection.execute(stmt_insert_keyword, keyword_insert_params)
                    keyword_id = connection.execute(text("SELECT @@IDENTITY AS id;")).fetchone()[0]
                else:
                    keyword_id = result[0]
                    print(f"Token '{token_name}' already exists with ID: {keyword_id}")

                # Insert into the mapping table
                print(f"Mapping tweet ID {tweet_id} with token ID {keyword_id}...")
                mapping_params = {"tweet_id": tweet_id, "keyword_id": keyword_id}

                print(f"Checking if mapping between tweet ID {tweet_id} and token ID {keyword_id} already exists...")
                stmt_check_mapping = text("""
                SELECT 1 FROM TweetKeywordsMapping WHERE tweet_id = :tweet_id AND keyword_id = :keyword_id
                """)
                mapping_exists = connection.execute(stmt_check_mapping, mapping_params).fetchone()

                if not mapping_exists:
                    print(f"Mapping tweet ID {tweet_id} with token ID {keyword_id}...")
                    stmt_mapping = text("INSERT INTO TweetKeywordsMapping (tweet_id, keyword_id) VALUES (:tweet_id, :keyword_id);")
                    connection.execute(stmt_mapping, mapping_params)
                    print("Committing the changes to the database...")
                    connection.commit()
                else:
                    print(f"Mapping between tweet ID {tweet_id} and token ID {keyword_id} already exists. Skipping...")

                    print("Committing the changes to the database...")
                    connection.commit()

    print("Finished processing tweets!")
    return "Processed successfully", 200


def main():    
    content = requests.get('http://157.90.130.44:58314/elonmusk.html').content

    tweets_data = extract_tweets_with_data(content)
    
    # test_data = [
    #         {
    #             'username': 'elonmusk',
    #             'timestamp': '2023-04-20T12:34:56Z',
    #             'text': 'Future 𝕏 company talks will be live-streamed so the public can watch too',
    #             'replies': '1K',
    #             'retweets': '2K',
    #             'likes': '3K'
    #         }
    #     ]

    # Pass the latest tweet to the store_and_process_tweets_core function
    
    latest_tweet = tweets_data[0] 
    # latest_tweet = test_data[0] 
    store_and_process_tweets_core([latest_tweet])

if __name__ == "__main__":
    main()