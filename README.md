# Turnstile

A simple anti-bot bot for Telegram groups.


# Idea

1. New user enters chat
2. Bot replies with greetings and link to the rules message X.
3. Rules message contains short rules info and accept/decline buttons.
4. If accepts within 1 minute, bot reply is deleted, user entered message is deleted.
5. Otherwise user is banned, all related messages are deleted.


# Solutions

1. Monitor chat for new user event