import datetime
import pickle
import re

import jsonpickle
import praw

from constants.Credentials import API
from constants.Globals import *
from constants.Tickers import *
from data import Comment as cmnt
from data import Submission as sub
from data import TickerData as td


# Get the time at which a submission was created
def get_date(submission):
    time = submission.created
    return datetime.datetime.fromtimestamp(time)


# Set a few rules for the comment being valid
def comment_is_valid(comment):
    # If the user deleted its post skip it
    if comment.author is None:
        return False

    # If the author name is a bot, ignore it.
    if comment.author.name in BOT_LIST:
        return False
    return True


# Set a few rules for the submission being valid
def submission_is_valid(submission):
    # If the user deleted its post skip it
    if submission.author is None:
        return False
    return True


# Search if the ticker exists in the given content
def has_ticker(content, ticker):
    if re.search('\\b' + ticker + '\\b', content):
        return True
    return False


# Gather all the comments in a submission
def gather_comments(submission):
    # List where comments will be stored
    comments = []

    # The replace_more method is used in order to get all the comments including the one where you'd have to expand
    # them manually by clicking "[+] more comments"
    submission.comments.replace_more(limit=None)

    # For each comment in the submission, if it's a valid comment, add it to the comments list
    for comment in submission.comments:
        if comment_is_valid(comment):
            comments.append(cmnt.Comment(author_name=comment.author.name,
                                         body=comment.body,
                                         ups=comment.ups))

    # Add the comments to the global COMMENTS list
    COMMENTS.extend(comments)

    # Return the comments list
    return comments


# Gather the submissions in a subreddit
def gather_submissions(subreddit):
    # Parse the specified number of submissions from the subreddit in the hot category
    for submission in subreddit.hot(limit=NR_OF_SUBMISSIONS):
        if submission_is_valid(submission):
            comments = gather_comments(submission)

            # Create a Submission object and add it to the SUBMISSIONS list
            SUBMISSIONS.append(sub.Submission(author_name=submission.author.name,
                                              comments=comments,
                                              date_time=get_date(submission),
                                              link_flair_text=submission.link_flair_text,
                                              selftext=submission.selftext,
                                              title=submission.title,
                                              upvotes=submission.ups,
                                              upvote_ratio=submission.upvote_ratio))


# Populate the TICKERDATA list with TickerData objects
def parse_data():
    # Loop through all tickers in the TICKERS list
    for ticker in TICKERS:
        submissions = []
        comments = []

        # Loop through all submissions and check if ticker was mentioned in the title or body
        for submission in SUBMISSIONS:
            if has_ticker(submission.title, ticker) or has_ticker(submission.selftext, ticker):
                submissions.append(submission)

        # Loop through all comments and check if ticker was mentioned in the comment
        for comment in COMMENTS:
            if has_ticker(comment.body, ticker):
                comments.append(comment)

        # Append ticker to the TICKERDATA list
        TICKERDATA.append(td.TickerData(ticker=ticker,
                                        comments=comments,
                                        submissions=submissions))


# Clean the data
def clean_data():
    for ticker_data in TICKERDATA:

        # Loop through all submissions and clean the data
        for submission in ticker_data.submissions:
            re.sub(r'[^\w\s]', '', submission.title)
            re.sub(r'[^\w\s]', '', submission.selftext)

        # Loop through all comments and clean the data
        for comment in ticker_data.comments:
            re.sub(r'[^\w\s]', '', comment.body)


# Save data in JSON format for later use
def save_data():
    # List of TickerData objects in string JSON format
    json_list = []

    # Use jsonpickle to create JSON strings from the object
    for ticker_data in TICKERDATA:
        json_obj = jsonpickle.encode(ticker_data)
        json_list.append(json_obj)

    # Pickle data for later
    with open('data.json', 'wb') as fp:
        pickle.dump(json_list, fp)


class Tickery:

    @staticmethod
    def main():
        print("Starting Tickery...")

        # Obtain reddit object
        reddit = praw.Reddit(
            client_id=API["client_id"],
            client_secret=API["client_secret"],
            user_agent=API["user_agent"])

        # Create a subreddit object
        subreddit = reddit.subreddit(SUBREDDIT_NAME)

        # Start gathering submissions
        print("Gathering content...")
        gather_submissions(subreddit)

        # Start searching for tickers
        print("Parsing data...")
        parse_data()

        # Clean the data
        print("Cleaning the data...")
        clean_data()

        # Save data in a JSON file
        print("Saving the data...")
        save_data()


if __name__ == "__main__":
    Tickery.main()
