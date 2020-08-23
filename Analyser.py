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


class Analyser:

    @staticmethod
    def main():
        print("Analysing data...")

        ticker_data_list = load_data()

        for ticker_data in ticker_data_list:
            final_score = 0

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

            print(ticker_data.ticker + " : " + str(final_score))


if __name__ == "__main__":
    Analyser.main()
