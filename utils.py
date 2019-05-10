import logging

from telegram.error import BadRequest

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def error_handler(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def delete_message_if_exists(bot, chat_id, msg_id):
    try:
        bot.delete_message(chat_id=chat_id, message_id=msg_id)
    except BadRequest as e:
        if hasattr(e, "message") and "not found" in e.message:
            return
        raise
