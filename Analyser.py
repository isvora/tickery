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

        # Calls for this ticker
        calls = []

        # Puts for this ticker
        puts = []

        # The sentiment score for this ticker
        final_score = 0

        # Number of mentions for the ticker
        nr_of_comments = ticker_data.number_of_occurrences_per_comment()
        nr_of_submissions = ticker_data.number_of_occurrences_per_submission()

        for submission in ticker_data.submissions:

            score = 0

            if ticker_data.ticker in submission.title:
                # Calculate the sentiment of the submission title
                score = sentiment_analysis(submission.title, submission.upvotes)

                # Check for call/put options mentioned in the submission title
                call = call_screener(ticker_data.ticker, submission.title)
                put = put_screener(ticker_data.ticker, submission.title)

                # If any are found, append them to the list
                if call is not None:
                    calls.append(call)

                if put is not None:
                    puts.append(put)

            if ticker_data.ticker in submission.selftext:
                # Calculate the sentiment of the submission body
                score = sentiment_analysis(submission.selftext, submission.upvotes)

                # Check for call/put options mentioned in the submission body
                call = call_screener(ticker_data.ticker, submission.selftext)
                put = put_screener(ticker_data.ticker, submission.selftext)

                # If any are found, append them to the list
                if call is not None:
                    calls.append(call)

                if put is not None:
                    puts.append(put)

            # Add the score to the final score of the ticker
            final_score = final_score + score

        for comment in ticker_data.comments:
            # Calculate the sentiment of the comment
            score = sentiment_analysis(comment.body, comment.ups)

            # Check for call/put options mentioned in the comment
            call = call_screener(ticker_data.ticker, comment.body)
            put = put_screener(ticker_data.ticker, comment.body)

            # If any are found, append them to the list
            if call is not None:
                calls.append(call)

            if put is not None:
                puts.append(put)

            # Add the score to the final score of the ticker
            final_score = final_score + score

        # Visualise only the first 2 digits after the dot
        visual_final_score = "%.2f" % final_score

        print(ticker_data.ticker + ": \t" + visual_final_score + " \tComments: " + str(
            nr_of_comments) + " \tSubmissions: " + str(nr_of_submissions) + " \tCalls: " + ' '.join(calls) +
              " \tPuts: " + ' '.join(puts))


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


# Search for calls in the given text
def call_screener(ticker, text):
    call_regex = create_regex(ticker, "C")
    return search_option(call_regex, text)


# Search for puts in the given text
def put_screener(ticker, text):
    put_regex = create_regex(ticker, "P")
    return search_option(put_regex, text)


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


if __name__ == "__main__":
    Analyser.main()
