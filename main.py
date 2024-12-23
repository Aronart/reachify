import time

from instaloader import InstaloaderException

from instaloader_handler import InstaLoaderHandler
from selenium_handler import SeleniumHandler
from database import DatabaseHandler
import random

# User details (for testing)
USERNAME = 'reachify.now'
PASSWORD = '%pfH.9+bzMsbT3i'

#SHORTCODE = 'DB1P4aVtitx'
SHORTCODE = 'DB6uEeiRo4u'
POST_URL = f'https://www.instagram.com/p/{SHORTCODE}/'

# Initialize modules
db = DatabaseHandler()
selenium_handler = SeleniumHandler(USERNAME, PASSWORD)

session_file = "session-instagram.txt"
insta_handler = InstaLoaderHandler(USERNAME, PASSWORD, session_file)

def main():
    # insta_handler = InstaLoaderHandler(USERNAME, PASSWORD, session_file)
    #
    # try:
    #     # Login or load session
    #     insta_handler.login()
    #
    #     # Get likes and comments
    #     likes, comments = insta_handler.get_post_likes_and_comments(SHORTCODE)
    #
    #     # Display results
    #     print("Likes:")
    #     for like in likes:
    #         print(f"- {like}")
    #
    #     print("\nComments:")
    #     for comment in comments:
    #         print(f"- {comment}")
    #
    # except InstaloaderException as e:
    #     print(f"An error occurred: {e}")

    try:
        # Log in to Instagram via Selenium
        selenium_handler.login()
        print('Done logging in')

        # Navigate to the post
        selenium_handler.navigate_to_post(POST_URL)

        # Fetch likes and comments
        likes = selenium_handler.get_likes(SHORTCODE)
        comments = selenium_handler.get_comments()

        # Save participants to database
        for username in likes:
            liked = True
            commented = username in comments
            reposted = False  # Adjust logic if repost checks are added

            db.add_or_update_participant(username, liked, commented, reposted)

        print("All participants added to database.")

    finally:
        db.close()
        # selenium_handler.close()

if __name__ == "__main__":
    main()