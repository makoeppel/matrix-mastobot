## matrix-mastobot

Matrix Bot written in python using [mastodon.py](https://github.com/halcy/Mastodon.py) and [simplematrixbotlib](https://github.com/i10b/simplematrixbotlib) served with [docker](https://www.docker.com/).

The main idea is to create a mastodon integration of the timeline via a Matrix Bot. For now the DM functions are not scheduled.

## (uncomplete) Feature list:
- Basic Functions:
    - [x] Getting timeline from mastodon via mastodon.py
    - [x] Showing last timeline entry on local flask server
    - [x] Showing last timeline in chat
    - [x] Reaload timeline
    - [x] Sort timeline by created_at

- Automation:
    - [] Automated timeline reload in the background
    - [] Automated timeline streaming to chat

- E2E:
    - [] Use E2E of [simplematrixbotlib](https://github.com/i10b/simplematrixbotlib)
    - [] E2E between bot and mastodon

- Search / Following:
    - [] Hashtag search
    - [] Mastodon user
    - [] Follow other user

- Dokumentation:
    - [x] List features
    - [] Installation dokumentation

- Tests / Error handling:
    - [x] Static code analysis with pylint
    - [] Unit tests
    - [] Simple error handling for connections

- Docker Setup:
    - [] Create simple docker container
    - [] Integrate into [matrix-docker-ansible-deploy](https://github.com/spantaleev/matrix-docker-ansible-deploy)

- UI:
    - [x] Simple Markdown timeline
    - [] Use icons (↩️, 🔄 and ⭐️) for reblog and favourite buttons

## Buy me a coffee

[paypal](https://www.paypal.me/makoeppel/)
