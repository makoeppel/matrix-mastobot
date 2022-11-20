"""
    Class file for the mastobot
"""

import os
import asyncio
import threading
import time
import simplematrixbotlib as botlib

from mastodon import Mastodon
from flask import Flask
from util.helpers import save_json, load_json


class Mastobot:
    """
        Bot class to connect to mastodon instance
        and forward timeline to matrix server.
    """
    def __init__(self, config, path=".cache/"):
        self.config = config
        self.path = path
        self._setup()

        # default values
        self.timeline_home = None
        self.timeline_local = None
        self.timeline_public = None
        self.mastodon = None
        self.mastobot = None

    def _setup(self):
        """
            Create .cache folder
        """
        # create cache folder if it's not there
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def connect_mastodon(self):
        """
            Create app connection to mastodon
        """
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

        self._log_in()

    def _log_in(self):
        # login to your mastodon server
        # and get the user token
        self.mastodon.log_in(
            self.config["mastodon-user"]["user_mail"],
            self.config["mastodon-user"]["user_password"],
            to_file = self.config["mastodon-user"]["token"]
        )

    def load_timeline(self, timeline=""):
        """
            load a specific timeline from mastodon, load the local
            stored timeline, check if we have new toots if so store them
            in self.timeline_NAME variable
        """
        if timeline == "home":
            curTimeline = self.mastodon.timeline_home()
        if timeline == "local":
            curTimeline = self.mastodon.timeline_local()
        if timeline == "public":
            curTimeline = self.mastodon.timeline_public()

        if not os.path.exists(self.path + f"timeline_{timeline}.json"):
            self.timeline_home = {}
            for toot in curTimeline:
                self.timeline_home[toot["created_at"].strftime('%Y/%m/%d %H:%M:%S')] = toot
            save_json(self.path + f"timeline_{timeline}.json", self.timeline_home)
        if os.path.exists(self.path + f"timeline_{timeline}.json"):
            self.timeline_home = {}
            loaded_timeline = load_json(self.path + f"timeline_{timeline}.json")
            for toot in curTimeline:
                if toot["created_at"].strftime('%Y/%m/%d %H:%M:%S') not in loaded_timeline:
                    loaded_timeline[toot["created_at"].strftime('%Y/%m/%d %H:%M:%S')] = toot
                    self.timeline_home[toot["created_at"].strftime('%Y/%m/%d %H:%M:%S')] = toot
            save_json(self.path + f"timeline_{timeline}.json", loaded_timeline)

    def load_timelines(self, timeline=""):
        """
            load all timelines (most recent ones first).
            The function can load the 'home', 'local', 'public'
            timesline via "" into the class attributes or return a
            specific one using 'home', 'local', 'public', 'tag/hashtag' or 'list/id'
        """
        self._log_in()

        # load all timelines and store in the class
        if timeline == "":
            for name in ["home", "local", "public"]:
                self.load_timeline(name)

        # load a specific timeline
        if timeline != "":
            self.load_timeline(timeline)

    def _sort_timeline(self, timeline):
        """
            Function to sort the timeline by created_at
        """
        created_list = []
        for toot in timeline:
            created_list.append(toot["created_at"].strftime('%Y/%m/%d %H:%M:%S'))

        _, timeline = (list(x) for x in zip(*sorted(
            zip(created_list, timeline),
            key=lambda pair: pair[0]
        )))

        return timeline

    def _clear_cache_folder(self):
        """
            Function to clear local cache / logging of bot
        """
        raise NotImplementedError(self.__class__.__name__ + '._clear_cache_folder()')

    def _search_mastodon(self, query=""):
        """
            Function to handle search request to mastodon
            using mastodon.search(query)
        """
        raise NotImplementedError(self.__class__.__name__ + '._search_mastodon()')

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

    def _convert_to_markdown(self, toots):
        """
            Function to convert timeline dicts to nice markdown
            Markdown Toot Template setup:

            ------------------------  ["account"]["username"]
            |["account"]["avatar"] |  ["account"]["url"]
            ------------------------
            ["content"]
            ["created_at"] ["replies_count"] ["reblogs_count"] ["reblogs_count"]
            ["url"]
        """
        output = ""
        for toot in toots.values():
            output += f"""
-------------------------------------------------------------------------------
{toot["content"]}
User: {toot["account"]["username"]} Created: {toot["created_at"].strftime('%Y/%m/%d %H:%M:%S')}  ↩️ {toot["replies_count"]}  🔄 {toot["reblogs_count"]}  ⭐️ {toot["favourites_count"]}
"""
            for i, media in enumerate(toot["media_attachments"]):
                output += f"""
Media{i}: {media["preview_url"]}
"""
            output += f"""[toot link]({toot["url"]})
-------------------------------------------------------------------------------
"""
        return output

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
        prefix = "!"

        # Help
        @self.mastobot.listener.on_message_event
        async def print_help(room, message):
            match = botlib.MessageMatch(room, message, self.mastobot, prefix)
            if match.is_not_from_this_bot() and match.prefix() and match.command("help"):
                help_message = """
                Help:
                - !help opens this menu
                - !echo your message
                - !local your local mastodon timeline
                - !home your home mastodon timeline
                - !public your public mastodon timeline
                - !reload load your current timeline
                - !cron start cron jobs to reaload timeline
                """
                await self.mastobot.api.send_markdown_message(room.room_id, help_message)

        # get local mastodon timeline
        @self.mastobot.listener.on_message_event
        async def local(room, message):
            match = botlib.MessageMatch(room, message, self.mastobot, prefix)
            if match.is_not_from_this_bot() and match.prefix() and match.command("local"):
                if len(self.timeline_local.keys()) > 0:
                    await self.mastobot.api.send_markdown_message(
                        room.room_id,
                        self._convert_to_markdown(self.timeline_local)
                    )

        # get home mastodon timeline
        @self.mastobot.listener.on_message_event
        async def home(room, message):
            match = botlib.MessageMatch(room, message, self.mastobot, prefix)
            if match.is_not_from_this_bot() and match.prefix() and match.command("home"):
                if len(self.timeline_home.keys()) > 0:
                    await self.mastobot.api.send_markdown_message(
                        room.room_id,
                        self._convert_to_markdown(self.timeline_home)
                    )

        # get public mastodon timeline
        @self.mastobot.listener.on_message_event
        async def public(room, message):
            match = botlib.MessageMatch(room, message, self.mastobot, prefix)
            if match.is_not_from_this_bot() and match.prefix() and match.command("public"):
                if len(self.timeline_public.keys()) > 0:
                    await self.mastobot.api.send_markdown_message(
                        room.room_id,
                        self._convert_to_markdown(self.timeline_public)
                    )

        # reload mastodon timelines
        @self.mastobot.listener.on_message_event
        async def reload(room, message):
            match = botlib.MessageMatch(room, message, self.mastobot, prefix)
            if match.is_not_from_this_bot() and match.prefix() and match.command("reload"):
                self.load_timelines()
                await self.mastobot.api.send_text_message(
                    room.room_id, "I have reloaded your timelines for you."
                )

        # Echo
        @self.mastobot.listener.on_message_event
        async def echo(room, message):
            """
            Example function that "echoes" arguements.
            Usage:
            user:  !echo say something
            bot:   say something
            """
            match = botlib.MessageMatch(room, message, self.mastobot, prefix)
            if match.is_not_from_this_bot() and match.prefix() and match.command("echo"):
                await self.mastobot.api.send_text_message(
                        room.room_id,
                        " ".join(arg for arg in match.args())
                )

        # create run job function which runs in a second thread
        @self.mastobot.listener.on_message_event
        async def cronjob(room, message):
            match = botlib.MessageMatch(room, message, self.mastobot, prefix)
            if match.is_not_from_this_bot() and match.prefix() and match.command("cron"):
                def run_cronbot():
                    async def cron_job():
                        api = botlib.Api(creds, config)
                        async_client = api.async_client
                        while True:
                            self.load_timelines()
                            await api.login()
                            await async_client.sync(timeout=65536, full_state=False)
                            if len(self.timeline_home.keys()) > 0:
                                await self.mastobot.api.send_markdown_message(
                                    room.room_id,
                                    self._convert_to_markdown(self.timeline_home)
                                )
                            time.sleep(5)
                    asyncio.run(cron_job())
                thread = threading.Thread(target=run_cronbot, daemon=True)
                thread.start()

        # run the bot
        self.mastobot.run()
