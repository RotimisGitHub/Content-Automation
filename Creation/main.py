import json
from datetime import datetime, timedelta
from moviepy.config import change_settings
from dotenv import load_dotenv
from praw import Reddit
from ScriptCreation import Script
import os
import praw
from python_to_postgres import PGHandler

load_dotenv(".env")
change_settings({"FFMPEG_BINARY": "/opt/anaconda3/envs/youtube_automation/bin/ffmpeg"})


class RedditSurfer:
    def __init__(self, reddit_query, limit):
        self.reddit = self._redditInitCredentials()
        self.reddit_query = reddit_query
        self.database = PGHandler("reddit_data")
        # Get the 'hot' submissions from the specified subreddit
        self.subreddit = self.reddit.subreddit(self.reddit_query).hot(limit=limit)

    def _redditInitCredentials(self):
        """
        Initialize Reddit credentials using predefined values from environment variables.

        Returns:
            praw.Reddit: An authenticated Reddit API instance.
        """

        CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
        CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET")
        USER_AGENT = 'Youtube by Tjserves'
        PASSWORD = os.environ.get("REDDIT_PASSWORD")
        USERNAME = 'Tjserves'

        reddit = Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=USER_AGENT,
            username=USERNAME,
            password=PASSWORD
        )
        return reddit

    def is_user_moderator(self, username):
        subreddit = self.reddit.subreddit(self.reddit_query)

        moderators = subreddit.moderator()

        return username in [i.name for i in moderators]

    def validated_stories(self):
        database = self.database.field_checker("reddit_id")

        database_ids = []

        if database is not None:
            # Normalize the retrieved database IDs (remove any non-alphanumeric characters)
            for id in database:
                new_id = "".join([i for i in str(id) if (str(i).isalnum())])
                database_ids.append(new_id)

            # Get a list of submissions whose IDs are not already in the database
            list_of_ids = [submission.id for submission in self.subreddit if submission.id not in database_ids]

            # Count and notify the user about duplicate submissions
            duplicates = len([submission.id for submission in self.subreddit if submission.id in database_ids])
            if duplicates == 0:
                print(f"Found {duplicates} matches in database.")
            else:
                print(f"Found {duplicates} matches in database. Will not create stories on duplicates!")
        else:
            # If the database is empty or not found, consider all submissions
            list_of_ids = [submission.id for submission in self.subreddit]

        return list_of_ids

    def gatherRedditContent(self, lengthOftext=1000):
        """
        Gather relevant content from a specified Reddit subreddit based on user-defined parameters such as post length
        and upvote ratio. Filters out posts already present in the database to avoid duplicates.

        Args:
            subreddit_q (str): The name of the subreddit from which to gather content. This should be a valid subreddit name.
            limit (int): The maximum number of posts to retrieve from the subreddit. Limits the number of submissions in the
                         'hot' category.
            lengthOftext (int, optional): The minimum required character count of the submission text (selftext). Only posts
                                          with a selftext of this length or more will be included. Defaults to 400 characters.
            upvoteRatio (float, optional): The minimum required upvote ratio for submissions to be included. Only posts with
                                           an upvote ratio equal to or higher than this will be considered. Defaults to 0.40.

        Returns:
            list of dict: A list of dictionaries, each representing a post that meets the criteria. Each dictionary contains:
                - 'Author' (str): The Reddit username of the post's author.
                - 'Title' (str): The title of the Reddit post.
                - 'Story' (str): The body of the post (selftext) with newlines removed.
                - 'Id' (str): The unique Reddit ID for the submission.
                - 'Url' (str): The URL of the post on Reddit.
                - 'subreddit query' (str): The name of the subreddit from which the post was retrieved.

        Notes:
            - This function utilizes a Postgres database handler to avoid gathering duplicate content. It checks if a post
              with the same Reddit ID already exists in the database and exc ludes it from the result if found.
            - The function retrieves submissions from the 'hot' category of the subreddit, meaning it prioritizes trending
              or popular posts within the defined `limit`.
            - Posts without the required length of selftext or a sufficient upvote ratio are automatically filtered out.

        Example Usage:
            - To gather the top 10 posts from the 'askreddit' subreddit with a minimum text length of 500 characters
              and an upvote ratio of at least 0.50:

              posts = gatherRedditContent('askreddit', limit=10, lengthOftext=500, upvoteRatio=0.50)
        """

        # Prepare the final list of posts that meet the criteria
        posts = []

        for submission_id in self.validated_stories():

            sub = self.reddit.submission(submission_id)
            if sub.score > 0:
                score = sub.score
                upvote_ratio = sub.upvote_ratio
                total_votes = score / (2 * upvote_ratio - 1)
                positive_votes = upvote_ratio * total_votes

            else:
                continue
            # Only add posts that meet the minimum text length and upvote ratio criteria
            if len(sub.selftext) >= lengthOftext and not self.is_user_moderator(sub.author):
                post = {
                    'Author': str(sub.author),
                    'Title': sub.title,
                    'Story': str(sub.selftext).replace("\n", ''),
                    "Id": submission_id,
                    'Url': sub.url,
                    "subreddit query": self.reddit_query
                }
                print(post)
                posts.append(post)

        return posts

    def execute(self):
        for data in self.gatherRedditContent():
            script = Script(reddit_query, data)
            script.create_tiktok_clips()


if __name__ == "__main__":
    reddit_query = "cheating_stories"
    limit = 20
    redditCrawler = RedditSurfer(reddit_query, limit)
    redditCrawler.execute()

# subreddits = ["AmITheAsshole", 'nosleep', 'pettyrevenge', 'badpeoplestories', 'cheating_stories',
#               'BestofRedditorUpdates']
#
