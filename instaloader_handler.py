import instaloader
import os

class InstaLoaderHandler:
    def __init__(self, username, password, session_file):
        self.username = username
        self.password = password
        self.session_file = session_file
        self.loader = instaloader.Instaloader()

    def login(self):
        # Check if session file exists
        if os.path.exists(self.session_file):
            # Load session from file if it exists
            try:
                self.loader.load_session_from_file(self.username, self.session_file)
                print("Session loaded from file.")
            except Exception as e:
                print(f"Failed to load session from file: {e}")
                self.create_and_save_session()
        else:
            # If no session file, prompt for login and save session
            self.create_and_save_session()

    def create_and_save_session(self):
        # Prompt for password and login
        # self.loader.login(self.username, input("Enter Instagram password: "))
        self.loader.login(self.username, self.password)
        # Save session to file for future use
        self.loader.save_session_to_file(self.session_file)
        print("Logged in and session saved.")

    def get_post_likes_and_comments(self, shortcode):
        post = instaloader.Post.from_shortcode(self.loader.context, shortcode)
        likes = [like.username for like in post.get_likes()]
        comments = [comment.owner.username for comment in post.get_comments()]

        print(f"Likes: {likes}")
        print(f"Comments: {comments}")

        return likes, comments