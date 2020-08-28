import pickle
import re

import jsonpickle
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer


# Load data from json file
def load_data():
    # List of TickerData objects
    ticker_data_list = []

    # Load the content from data.json
    with open('data.json', 'rb') as fp:
        json_list = pickle.load(fp)

    # Loop through the content and use jsonpickle to create objects
    for ticker_data in json_list:
        ticker_data_list.append(jsonpickle.decode(ticker_data))

    # Return the list of TickerData objects
    return ticker_data_list


# Remove stop words from the given text
def remove_stop_words(content_list):
    final_list = []
    for word in content_list:
        if word not in stopwords.words('english'):
            final_list.append(word)
    return final_list


# Update lexicon
def update_lexicon():
    new_words = {
        'bull': 3.0,
        'call': 3.0,
        'calls': 3.0,
        'put': -3.0,
        'bear': -3.0,
    }

    SIA = SentimentIntensityAnalyzer()

    SIA.lexicon.update(new_words)


# Calculate sentiment analysis
def sentiment_analysis(text, upvote):
    score = SentimentIntensityAnalyzer().polarity_scores(text)
    neg = score['neg']
    pos = score['pos']

    if upvote == 0:
        upvote = 1

    if neg > pos:
        return neg * upvote * -1
    else:
        return pos * upvote


# Analyse the data
def analyse_data(ticker_data_list):
    for ticker_data in ticker_data_list:

        # The sentiment score for this ticker
        final_score = 0

        # Number of mentions for the ticker
        nr_of_comments = ticker_data.number_of_occurrences_per_comment()
        nr_of_submissions = ticker_data.number_of_occurrences_per_submission()

        for submission in ticker_data.submissions:
            score = 0
            if ticker_data.ticker in submission.title:
                score = sentiment_analysis(submission.title, submission.upvotes)
            if ticker_data.ticker in submission.selftext:
                score = sentiment_analysis(submission.selftext, submission.upvotes)
            final_score = final_score + score

        for comment in ticker_data.comments:
            score = sentiment_analysis(comment.body, comment.ups)
            final_score = final_score + score

        # Visualise only the first 2 digits after the dot
        visual_final_score = "%.2f" % final_score

        print(ticker_data.ticker + " : \t" + visual_final_score + " \tComments: \t" + str(
            nr_of_comments) + " \tSubmissions: \t" + str(nr_of_submissions))


# Search for the given regex in the given string and return it if it's found
def search_option(regex, text):
    p = re.compile(regex)
    result = p.search(text)
    if result is not None:
        return result.group(0)

    return None


# Create regex string for options
def create_regex(ticker, option):
    return "(" + ticker + ") [0-9]*" + option + " [0-9]*/[0-9]*"


# Seek for options
# An option is either a call or a put with an expiration date and a strike price
# Example: TSLA 2500C 08/28 -> Tesla call with a 2500 strike price expiring on 28 August
def option_screener(ticker_data_list):
    calls = []
    puts = []
    for ticker_data in ticker_data_list:
        ticker = ticker_data.ticker
        call_regex = create_regex(ticker, "C")
        put_regex = create_regex(ticker, "P")

        for submission in ticker_data.submissions:
            call = search_option(call_regex, submission.selftext)
            put = search_option(put_regex, submission.selftext)

            if call is not None:
                calls.append(call)

            if put is not None:
                puts.append(put)

            call = search_option(call_regex, submission.title)
            put = search_option(put_regex, submission.title)

            if call is not None:
                calls.append(call)

            if put is not None:
                puts.append(put)

        for comment in ticker_data.comments:
            call = search_option(call_regex, comment.body)
            put = search_option(put_regex, comment.body)

            if call is not None:
                calls.append(call)

            if put is not None:
                puts.append(put)

    print("Calls:")
    for call in calls:
        print(call)

    print("Puts:")
    for put in puts:
        print(put)


class Analyser:

    @staticmethod
    def main():
        print("Analysing data...")

        # Load the data from the json file
        ticker_data_list = load_data()

        # Update the vader sentiment lexicon
        update_lexicon()

        # Analyse data
        analyse_data(ticker_data_list)

        # Search for options
        option_screener(ticker_data_list)


if __name__ == "__main__":
    Analyser.main()
