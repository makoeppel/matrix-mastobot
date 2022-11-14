import yaml
from src.bot import mastobot


# open the config file
with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)

# create mastobot instance
mastobot = mastobot(config)

# connect to mastodon
mastobot.connect_mastodon()

# load timelines
mastobot.load_timelines()

# setup flask server for testing without matrix
#mastobot.run_flask()

# run matrix bot
mastobot.run()
