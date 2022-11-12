from mastodon import Mastodon
from flask import Flask
from util.helpers import *
import os

import subprocess
import simplematrixbotlib as botlib
from urllib.request import ssl, socket
import datetime, smtplib



class mastobot:
    """
        Bot class to connect to mastodon instance
        and forward timeline to matrix server.
    """
    def __init__(self, config, path=".cache/"):
        self.config = config
        self.path = path
        self._setup()

    def _setup(self):
        # create cache folder if it's not there
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def connect_mastodon(self):
        # check if file pytooter_clientcred.secret exists
        # otherwise register the APP
        if not os.path.exists(self.config["mastodon-user"]["secret"]):
            Mastodon.create_app(
                'matrix-mastodon-bot', # NOTE: maybe we make this dynamic with user name?
                api_base_url = self.config["mastodon-user"]["api_base_url"],
                to_file = self.config["mastodon-user"]["secret"]
            )

        # create mastodon instance
        self.mastodon = Mastodon(
            client_id = self.config["mastodon-user"]["secret"],
            api_base_url = self.config["mastodon-user"]["api_base_url"]
        )

        # login to your mastodon server
        # and get the user token
        self.mastodon.log_in(
            self.config["mastodon-user"]["user_mail"],
            self.config["mastodon-user"]["user_password"],
            to_file = self.config["mastodon-user"]["token"]
        )

    def load_timelines(self, timeline="", reload=False):
        """
            load all timelines (most recent ones first). 
            The function can load the 'home', 'local', 'public' 
            timesline via "" into the class attributes or return a 
            specific one using 'home', 'local', 'public', 'tag/hashtag' or 'list/id'
        """
        # load all timelines and store in the class
        if timeline == "":
            # handle home timeline
            if os.path.exists(self.path + "timeline_home.json") and not reload:
                self.timeline_home = load_json(self.path + "timeline_home.json")
            if not os.path.exists(self.path + "timeline_home.json") or reload:
                self.timeline_home = self.mastodon.timeline_home()
                save_json(self.path + "timeline_home.json", self.timeline_home)

            # handle local timeline
            if os.path.exists(self.path + "timeline_local.json") and not reload:
                self.timeline_local = load_json(self.path + "timeline_local.json")
            if not os.path.exists(self.path + "timeline_local.json") or reload:
                self.timeline_local = self.mastodon.timeline_local()
                save_json(self.path + "timeline_local.json", self.timeline_local)

            # handle public timeline
            if os.path.exists(self.path + "timeline_public.json") and not reload:
                self.timeline_public = load_json(self.path + "timeline_public.json")
            if not os.path.exists(self.path + "timeline_public.json") or reload:
                self.timeline_public = self.mastodon.timeline_public()
                save_json(self.path + "timeline_public.json", self.timeline_public)
        
        print("Done")

        # load a specific timeline
        if timeline != "":
            return self.mastodon.timeline(timeline=timeline)

    def _clear_cache_folder(self):
        """
            Function to clear local cache / logging of bot
        """
        pass

    def _search_mastodon(self, query=""):
        """
            Function to handle search request to mastodon
            using mastodon.search(query)
        """
        pass

    def run_flask(self):
        """
            Use a local flask server to test the bot instead of
            having an actual matrix server running
        """
        # start flask app
        app = Flask(__name__)

        @app.route("/")
        def hello_world():
            return self.timeline_home[0]["content"]

        app.run(debug=True)

    def _get_timeline(self, timeline=""):
        """
            Create markdown from local timeline
        """
        if timeline == "local":
            return self.timeline_local[-1]["content"]
        if timeline == "home":
            return self.timeline_home[-1]["content"]
        if timeline == "public":
            return self.timeline_public[-1]["content"]

    def run(self):
        """
            Function which is running the actual matrix mastobot
        """
        # create creds for the bot
        creds = botlib.Creds(
            self.config["matrix"]["matrix_url"],
            self.config["matrix"]["bot_user"],
            self.config["matrix"]["bot_password"]
        )

        # create config for the bot
        config = botlib.Config()
        config.join_on_invite = True

        # create bot
        self.mastobot = botlib.Bot(creds, config)

        # prefix for the bot
        PREFIX = "!"

        # Help
        @self.mastobot.listener.on_message_event
        async def help(room, message):
            match = botlib.MessageMatch(room, message, self.mastobot, PREFIX)
            if match.is_not_from_this_bot() and match.prefix() and match.command("help"):
                help_message = """
                Help:
                - !help opens this menu
                - !echo your message
                - !local your local mastodon timeline
                - !home your home mastodon timeline
                - !public your public mastodon timeline
                - !reload load your current timeline
                """
                await self.mastobot.api.send_markdown_message(room.room_id, help_message)

        # get local mastodon timeline
        @self.mastobot.listener.on_message_event
        async def local(room, message):
            match = botlib.MessageMatch(room, message, self.mastobot, PREFIX)
            if match.is_not_from_this_bot() and match.prefix() and match.command("local"):
                await self.mastobot.api.send_markdown_message(
                    room.room_id, 
                    self._get_timeline("local")
                )

        # get home mastodon timeline
        @self.mastobot.listener.on_message_event
        async def home(room, message):
            match = botlib.MessageMatch(room, message, self.mastobot, PREFIX)
            if match.is_not_from_this_bot() and match.prefix() and match.command("home"):
                await self.mastobot.api.send_markdown_message(
                    room.room_id, 
                    self._get_timeline("home")
                )

        # get public mastodon timeline
        @self.mastobot.listener.on_message_event
        async def public(room, message):
            match = botlib.MessageMatch(room, message, self.mastobot, PREFIX)
            if match.is_not_from_this_bot() and match.prefix() and match.command("public"):
                await self.mastobot.api.send_markdown_message(
                    room.room_id, 
                    self._get_timeline("public")
                )

        # reload mastodon timelines
        @self.mastobot.listener.on_message_event
        async def reload(room, message):
            match = botlib.MessageMatch(room, message, self.mastobot, PREFIX)
            if match.is_not_from_this_bot() and match.prefix() and match.command("reload"):
                self.load_timelines(reload=True)
                await self.mastobot.api.send_text_message(room.room_id, "I have reloaded your timelines for you.")

        # Echo
        @self.mastobot.listener.on_message_event
        async def echo(room, message):
            """
            Example function that "echoes" arguements.
            Usage:
            user:  !echo say something
            bot:   say something
            """
            match = botlib.MessageMatch(room, message, self.mastobot, PREFIX)
            if match.is_not_from_this_bot() and match.prefix() and match.command("echo"):
                print("Room: {r}, User: {u}, Message: {m}".format(r=room.room_id, u=str(message).split(':')[0], m=str(message).split(':')[-1].strip()))
                await self.mastobot.api.send_text_message(room.room_id, " ".join(arg for arg in match.args()))

        # run the bot
        self.mastobot.run()
