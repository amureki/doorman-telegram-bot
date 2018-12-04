import logging
import os
from time import sleep

from telegram.ext import Updater, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def new_member_handler(bot, update):
    msg = update.message
    for user in msg.new_chat_members:
        username = user.name
        bot_reply = bot.send_message(
            chat_id=msg.chat_id,
            text=f'Welcome, {username}!')
        sleep(60)
        bot.delete_message(chat_id=msg.chat_id, message_id=bot_reply.message_id)

    bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)


def start_bot():
    if not all([BOT_TOKEN]):
        raise ValueError(
            'One of the variables -'
            'BOT_TOKEN'
            'is missing in environment'
        )

    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    echo_handler = MessageHandler(Filters.status_update.new_chat_members, new_member_handler)
    dispatcher.add_handler(echo_handler)
    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    start_bot()
