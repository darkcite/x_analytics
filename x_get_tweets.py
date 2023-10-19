import requests
import json

def fetch_twitter_data():
    # Define the URL
    url = "https://twitter.com/i/api/graphql/VgitpdpNZ-RUIp5D1Z_D-A/UserTweets"

    # Extracted cookies and CSRF token

    # Define the headers
    headers = {
    }

    # Define the query parameters
    params = {
        'variables': '{"userId":"44196397","count":20,"includePromotedContent":true,"withQuickPromoteEligibilityTweetFields":true,"withVoice":true,"withV2Timeline":true}',
        'features': '{"responsive_web_graphql_exclude_directive_enabled":true,"verified_phone_label_enabled":false,"responsive_web_home_pinned_timelines_enabled":true,"creator_subscriptions_tweet_preview_api_enabled":true,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"c9s_tweet_anatomy_moderator_badge_enabled":true,"tweetypie_unmention_optimization_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"responsive_web_twitter_article_tweet_consumption_enabled":false,"tweet_awards_web_tipping_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":true,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":true,"longform_notetweets_rich_text_read_enabled":true,"longform_notetweets_inline_media_enabled":true,"responsive_web_media_download_video_enabled":false,"responsive_web_enhance_cards_enabled":false}'
    }
    # Make the GET request
    response = requests.get(url, headers=headers, params=params)
    
    # Write the output to a file
    with open('twitter_data_output.json', 'w') as file:
        # If you want to pretty-print the JSON response
        file.write(json.dumps(response.json(), indent=4))
        # If you want the raw response
        # file.write(response.text)
    
    return response.json()

def find_tweets_recursive(data, depth=1):
    """
    Recursively explore the JSON structure to find entries with 'full_text' key.
    """
    tweets = []

    if depth > 20:  # Limiting the recursion depth
        return tweets

    if isinstance(data, dict):
        # Check if the current dictionary has the 'full_text' key
        if "full_text" in data:
            tweets.append(data)
        else:
            # If not, recursively explore its values
            for value in data.values():
                tweets.extend(find_tweets_recursive(value, depth + 1))
    elif isinstance(data, list):
        # If the current data is a list, explore its items
        for item in data:
            tweets.extend(find_tweets_recursive(item, depth + 1))

    return tweets

def standardize_tweets(extracted_tweets):
    standardized_tweets = []

    for tweet in extracted_tweets:
        is_repost = 'retweeted_status' in tweet
        standardized_tweet = {
            'tweet_id': tweet['id_str'],
            'created_at': tweet['created_at'],
            'full_text': tweet['full_text'],
            'favorite_count': tweet['favorite_count'],
            'retweet_count': tweet.get('retweet_count', 0),
            'is_repost': is_repost,
            'entities': tweet['entities'],
        }
        if is_repost:
            standardized_tweet['original_author'] = tweet['retweeted_status']['user']['screen_name']
        standardized_tweets.append(standardized_tweet)

    # Ordering by 'created_at' in descending order inside the standardize_tweets function
    return sorted(standardized_tweets, key=lambda x: x['created_at'], reverse=True)

x_data = fetch_twitter_data()
extracted_tweets = find_tweets_recursive(x_data)
ordered_tweets = standardize_tweets(extracted_tweets)

print(ordered_tweets)
