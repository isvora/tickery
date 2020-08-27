import pickle

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

        print(ticker_data.ticker + " : " + visual_final_score + " Comments: " + str(
            nr_of_comments) + " Submissions: " + str(nr_of_submissions))


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
