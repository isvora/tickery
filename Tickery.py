import praw

from constants.Credentials import API


class Tickery:

    @staticmethod
    def main():

        print("Tickery")

        # Obtain reddit object
        reddit = praw.Reddit(
            client_id=API["client_id"],
            client_secret=API["client_secret"],
            user_agent=API["user_agent"])

        # Submissions list
        submissions_list = []


if __name__ == "__main__":
    Tickery.main()
