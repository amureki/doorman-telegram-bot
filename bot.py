import os
from time import sleep

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

BOT_TOKEN = os.environ.get("BOT_TOKEN")
SECONDS_BEFORE_KICK = 20


@run_async
def new_member_action(bot, update):
    msg = update.message
    chat_id = msg.chat_id
    for user in msg.new_chat_members:
        username = user.name
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
            text=f"{username}, пожалуйста, согласитесь с правилами группы (в пине и описании).",
            reply_markup=reply_markup,
        )

        sleep(SECONDS_BEFORE_KICK)
        user_info = bot.get_chat_member(chat_id=chat_id, user_id=user.id)

        delete_message_if_exists(bot=bot, chat_id=chat_id, msg_id=bot_reply.message_id)

        if user_info.can_send_messages is False:
            bot.kick_chat_member(chat_id=msg.chat_id, user_id=user.id)


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
    else:
        bot.kick_chat_member(chat_id=chat.id, user_id=user.id)

    bot.delete_message(chat_id=chat.id, message_id=bot_msg.message_id)


def start_bot():
    if not all([BOT_TOKEN]):
        raise ValueError(
            "One of the variables -" "BOT_TOKEN" "is missing in environment"
        )

    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    new_member_handler = MessageHandler(
        Filters.status_update.new_chat_members, new_member_action
    )
    dispatcher.add_handler(new_member_handler)

    dispatcher.add_handler(CommandHandler("rules", rules_command_handler))
    updater.dispatcher.add_handler(CallbackQueryHandler(rules_button_handler))

    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    start_bot()
