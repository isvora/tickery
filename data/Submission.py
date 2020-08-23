class Submission:

    def __init__(self, author_name, comments, date_time, link_flair_text, selftext, title, upvotes, upvote_ratio):
        self.id = author_name
        self.date_time = date_time
        self.comments = comments
        self.link_flair_text = link_flair_text
        self.selftext = selftext
        self.title = title
        self.upvotes = upvotes
        self.upvote_ratio = upvote_ratio
