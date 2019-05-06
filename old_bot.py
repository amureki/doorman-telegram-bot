import logging
import os
from time import sleep

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackQueryHandler, \
    run_async

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN')


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


@run_async
def new_member_action(bot, update):
    msg = update.message
    for user in msg.new_chat_members:
        username = user.name
        # TODO: get pinned message and append it's link to the bot reply
        bot.restrict_chat_member(
            chat_id=msg.chat_id,
            user_id=user.id
        )
        bot_reply = bot.send_message(
            chat_id=msg.chat_id,
            text=f'Welcome, {username}!')
        sleep(60)
        bot.delete_message(chat_id=msg.chat_id, message_id=bot_reply.message_id)

    bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)


def rules(bot, update):
    keyboard = [[
        InlineKeyboardButton('Согласен(-на) с правилами', callback_data='accept'),
        InlineKeyboardButton('Правила не по мне', callback_data='decline')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = '''
» Уважайте себя и других;
» dpaste.de, gist.github.com используйте для демонстрации кода, без скриншотов;
» github.com/amureki/django_faq - подробный FAQ группы;
» чат тематический, off-topic сообщения (не относящиеся к django) не разрешены;
» не спамьте сообщениями/стикерами/картинками/командами;
» работа и резюме в @django_jobs, флуд в @django_flood.
    '''
    update.message.reply_text(message, reply_markup=reply_markup)


def rules_button(bot, update):
    query = update.callback_query
    from_user = query.from_user

    answer = query.data
    if answer == 'accept':
        # TODO:
        pass
    else:
        pass
        bot.kick_chat_member(
            chat_id=query.message.chat_id,
            user_id=from_user.id
        )


def start_bot():
    if not all([BOT_TOKEN]):
        raise ValueError(
            'One of the variables -'
            'BOT_TOKEN'
            'is missing in environment'
        )

    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    new_member_handler = MessageHandler(Filters.status_update.new_chat_members, new_member_action)
    dispatcher.add_handler(new_member_handler)

    dispatcher.add_handler(CommandHandler('rules', rules))
    updater.dispatcher.add_handler(CallbackQueryHandler(rules_button))

    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    start_bot()
