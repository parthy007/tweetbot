from textbase import bot, Message
from textbase.models import OpenAI
from typing import List
import tweepy
import os

# Load your OpenAI API key
OpenAI.api_key = os.getenv('API_KEY')


# Prompt for GPT-3.5 Turbo
SYSTEM_PROMPT = """ 
Extract the tweet the user want to make from the following message and don't make changes to it but feel free to add emojis and hashtags: 
"""

# Initial message to introduce the chatbot
INITIAL_MESSAGE = "Welcome to the Tweet Chatbot! I can help you compose tweets. Just send me the message you want to tweet, and I'll take care of the rest. Let's get started!"


# Use your Twitter API credentials
BEARER_TOKEN = ""
TWITTER_API_KEY = ""
TWITTER_API_SECRET = ""
TWITTER_ACCESS_TOKEN = ""
TWITTER_ACCESS_TOKEN_SECRET = ""

# Initialize Tweepy
client = tweepy.Client(BEARER_TOKEN, TWITTER_API_KEY, TWITTER_API_SECRET,
                       TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
auth = tweepy.OAuth1UserHandler(
    TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

initial_message_sent = False


@bot()
def on_message(message: List[Message], state: dict = None):

    global initial_message_sent

    if not state and not initial_message_sent:
        initial_message_sent = True  # Mark the initial message as sent
        # Send the initial message to introduce the chatbot
        response = {
            "data": {
                "messages": [
                    {
                        "data_type": "STRING",
                        "value": INITIAL_MESSAGE
                    }
                ],
                "state": {}
            },
            "errors": [
                {
                    "message": ""
                }
            ]
        }
        return {  # Return the initial message response immediately
            "status_code": 200,
            "response": response
        }

    user_message = message[-1]['content'][0]['value']

    # Send the entire user message to OpenAI to extract the tweet message
    response = OpenAI.generate(
        system_prompt=SYSTEM_PROMPT + user_message,
        message_history=message,
        max_tokens=50,  # Adjust as needed
        model="gpt-3.5-turbo",  # You can add a stop condition if necessary
    )

    generated_tweet = response

    # Try to tweet the message
    try:
        client.create_tweet(text=generated_tweet)
        bot_response = "Successfully tweeted: " + generated_tweet
    except tweepy.TweepError as e:
        bot_response = "Tweeting failed. Error: " + str(e)

    response = {
        "data": {
            "messages": [
                {
                    "data_type": "STRING",
                    "value": bot_response
                }
            ],
            "state": state
        },
        "errors": [
            {
                "message": ""
            }
        ]
    }

    return {
        "status_code": 200,
        "response": response
    }
