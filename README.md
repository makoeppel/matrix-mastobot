## matrix-mastobot

Matrix Bot written in python using [mastodon.py](https://github.com/halcy/Mastodon.py) and [simplematrixbotlib](https://github.com/i10b/simplematrixbotlib) served with [docker](https://www.docker.com/).

The main idea is to create a full mastodon integration of the timeline via a Matrix Bot. For now the DM functions are not scheduled.

## (uncomplete) Feature list:
- Basic Functions:
    - [x] getting timeline from mastodon via mastodon.py
    - [x] showing last timeline entry on local flask server
    - [x] showing last timeline in chat
    - [x] reaload timeline

- E2E:
    - [] use E2E of [simplematrixbotlib](https://github.com/i10b/simplematrixbotlib)
    - [] E2E between bot and mastodon

- Search / Following:
    - [] Hashtag search
    - [] Mastodon user
    - [] Follow other user

- Dokumentation:
    - [x] List features
    - [] Installation dokumentation

- Tests / Error handling:
    - [] Unit tests
    - [] Simple error handling for connections

- Docker Setup:
    - [] Create simple docker container
    - [] Integrate into [matrix-docker-ansible-deploy](https://github.com/spantaleev/matrix-docker-ansible-deploy)

## Buy me a coffee

[paypal](https://www.paypal.me/makoeppel/)
