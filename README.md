# Turnstile

A simple anti-bot bot for Telegram groups.

## Initial implementation

1. New user enters chat
2. Bot replies with greetings message and two buttons.
3. Message contains short rules info and accept/decline buttons.
4. If accepts within 1 minute, bot reply is deleted, user entered message is deleted.
5. Otherwise user is banned, all related messages are deleted.

## Future idea

1. New user enters chat
2. Bot replies with greetings and link to the rules message X.
3. Rules message contains short rules info and accept/decline buttons.
4. If accepts within 1 minute, bot reply is deleted, user entered message is deleted.
5. Otherwise user is banned, all related messages are deleted.

### Solution

- [x] 1. Monitor chat for new user event
- [x] 2. Send message to new user
- [ ] 3. Prepare pin message with buttons (should be created by bot)
- [ ] 4. Monitor button click event from new user
- [ ] 5. Ban user after period of time, remove all messages

