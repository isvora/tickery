class TickerData:

    def __init__(self, ticker, comments, submissions):
        self.ticker = ticker
        self.comments = comments
        self.submissions = submissions

    def number_of_occurrences_per_comment(self):
        return len(self.comments)

    def number_of_occurrences_per_submission(self):
        return len(self.submissions)
