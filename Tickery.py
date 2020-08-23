import datetime

import praw

from constants.Credentials import API
from constants.Globals import *
from data import Comment as cmnt
from data import Submission as sub


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

    # Return the comments list
    return comments


# Gather the submissions in a subreddit
def gather_submissions(subreddit):
    # Parse the specified number of submissions from the subreddit in the hot category
    for submission in subreddit.hot(limit=NR_OF_SUBMISSIONS):
        if "Discussion" not in submission.title:
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


class Tickery:

    @staticmethod
    def main():
        print("Tickery")

        # Obtain reddit object
        reddit = praw.Reddit(
            client_id=API["client_id"],
            client_secret=API["client_secret"],
            user_agent=API["user_agent"])

        # Create a subreddit object
        subreddit = reddit.subreddit(SUBREDDIT_NAME)

        # Start gathering submissions
        gather_submissions(subreddit)


if __name__ == "__main__":
    Tickery.main()
