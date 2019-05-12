import logging
import os

import requests
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
    run_async,
)

from utils import delete_message_if_exists, error_handler

logger = logging.getLogger(__name__)
sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    integrations=[LoggingIntegration(level=logging.INFO, event_level=logging.WARNING)],
    environment="doorman",
    server_name=os.environ.get("SERVER_NAME", "Undefined"),
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
SECONDS_BEFORE_KICK = os.environ.get("SECONDS_BEFORE_KICK", "60")
ENABLE_DEBUG_SENTRY_LOGGING = os.environ.get("ENABLE_DEBUG_SENTRY_LOGGING", False)
HEALTHCHECK_TOKEN = os.environ.get("HEALTHCHECK_TOKEN")


@run_async
def new_member_action(bot, update, job_queue):
    msg = update.message
    chat_id = msg.chat_id
    for user in msg.new_chat_members:
        if ENABLE_DEBUG_SENTRY_LOGGING:
            logger.warning(
                'Doorman is restricting user in "%s"',
                msg.chat.title,
                extra={"username": user.name, "chat_id": msg.chat_id},
            )

        # TODO: restrict only for 24 hours maybe?
        bot.restrict_chat_member(chat_id=chat_id, user_id=user.id)
        bot.delete_message(chat_id=chat_id, message_id=msg.message_id)

        keyboard = [
            [
                InlineKeyboardButton("Согласны", callback_data=f"accept__{user.id}"),
                InlineKeyboardButton("Нет", callback_data=f"decline__{user.id}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        bot_reply = bot.send_message(
            chat_id=chat_id,
            text=f"{user.name}, пожалуйста, согласитесь с правилами группы (в пине и описании).",
            reply_markup=reply_markup,
        )

        job_queue.run_once(
            kick_if_no_reaction,
            when=int(SECONDS_BEFORE_KICK),
            context={
                "chat_id": chat_id,
                "chat_title": msg.chat.title,
                "user_id": user.id,
                "bot_reply_id": bot_reply.message_id,
            },
        )


def kick_if_no_reaction(bot, job):
    chat_id = job.context["chat_id"]
    chat_title = job.context["chat_title"]
    user_id = job.context["user_id"]
    bot_reply_id = job.context["bot_reply_id"]

    user_info = bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    delete_message_if_exists(bot=bot, chat_id=chat_id, msg_id=bot_reply_id)
    if user_info.can_send_messages is False:
        if ENABLE_DEBUG_SENTRY_LOGGING:
            logger.warning(
                'Doorman is kicking user in "%s"',
                chat_title,
                extra={
                    "username": user_info.user.name,
                    "chat_id": chat_id,
                    "reason": "ignored",
                },
            )
        bot.kick_chat_member(chat_id=chat_id, user_id=user_id)


@run_async
def left_chat_member_action(bot, update):
    msg = update.message
    chat_id = msg.chat_id
    bot.delete_message(chat_id=chat_id, message_id=msg.message_id)


def rules_command_handler(bot, update):
    chat = bot.get_chat(chat_id=update.message.chat.id)
    rules_msg = chat.pinned_message.text
    update.message.reply_text(rules_msg)


def rules_button_handler(bot, update):
    query = update.callback_query
    callback_data = query.data

    new_user_id = int(callback_data.split("__")[1])

    chat = update.effective_chat
    user = update.effective_user
    bot_msg = update.callback_query.message

    if user.id != new_user_id:
        return

    if callback_data.startswith("accept"):
        bot.promote_chat_member(chat_id=chat.id, user_id=user.id)
        if ENABLE_DEBUG_SENTRY_LOGGING:
            logger.warning(
                'Doorman is promoting user in "%s"',
                chat.title,
                extra={"username": user.name, "chat_id": chat.id},
            )
    else:
        if ENABLE_DEBUG_SENTRY_LOGGING:
            logger.warning(
                'Doorman is kicking user in "%s"',
                chat.title,
                extra={"username": user.name, "chat_id": chat.id, "reason": "declined"},
            )
        bot.kick_chat_member(chat_id=chat.id, user_id=user.id)

    bot.delete_message(chat_id=chat.id, message_id=bot_msg.message_id)


def healthcheck_callback(bot, job):
    if HEALTHCHECK_TOKEN:
        requests.get("https://hc-ping.com/{}".format(HEALTHCHECK_TOKEN))


def start_bot():
    if not all([BOT_TOKEN]):
        raise ValueError(
            "One of the variables -" "BOT_TOKEN" "is missing in environment"
        )

    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # handlers
    new_member_handler = MessageHandler(
        Filters.status_update.new_chat_members, new_member_action, pass_job_queue=True
    )
    dispatcher.add_handler(new_member_handler)
    left_chat_member_handler = MessageHandler(
        Filters.status_update.left_chat_member, left_chat_member_action
    )
    dispatcher.add_handler(left_chat_member_handler)

    dispatcher.add_handler(CommandHandler("rules", rules_command_handler))
    dispatcher.add_handler(CallbackQueryHandler(rules_button_handler))

    dispatcher.add_error_handler(error_handler)

    # healthcheck
    updater.job_queue.run_repeating(healthcheck_callback, interval=60, first=0)

    # initialization
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    start_bot()
