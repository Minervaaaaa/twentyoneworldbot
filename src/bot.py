import logging
from textwrap import dedent
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update

import config

from database import setup_database
from taproot import taproot_handle_command
from mempool import block_time, mempool_space_mempool_stats, mempool_space_fees, halving
from price import fortune_teller, moscow_time, price, price_update_ath, sat_in_fiat
from einundzwanzig import episode, shoutout, memo, invoice, cancel, SHOUTOUT_AMOUNT, SHOUTOUT_MEMO, soundboard, \
    soundboard_button


def start_command(update: Update, context: CallbackContext):
    """
    Sends a welcome message to the user
    Should be customized in the future
    """

    welcome_message = dedent("""
    Hi, I am the TwentyOneWorldBot, the offical Telegram Bot of the TwentyOneWorld Community.


    Commands:
    /fee - Actual transcation fee.
    /mempool - Mempool visualization. Mempool. First element is the number of mempool blocks, max <i>8</i>.
    /price - price in USD, EUR and CHF.
    /halving - Time until next halving event.
    /satinfiat - <i>satoshis</i> Displays the fiat price of satoshis in USD, EUR and CHF.
    /block_time - Actual block time.
    /moscow_time - SAT per USD, SAT per EUR and SAT per CHF.
    /fortune_teller - price predication
    """)

    update.message.reply_text(text=welcome_message, parse_mode='HTML', disable_web_page_preview=True)


def taproot_command(update: Update, context: CallbackContext):
    """
    Calculates Taproot Activation Statistics
    """
    taproot_handle_command(update, context)


def fee_command(update: Update, context: CallbackContext):
    """
    Get fees for next blocks from mempool.space
    """
    mempool_space_fees(update, context)


def mempool_command(update: Update, context: CallbackContext):
    """
    Get current mempool stats
    """
    mempool_space_mempool_stats(update, context)


def block_time_command(update: Update, context: CallbackContext):
    """
    Get the current block time (block height)
    """
    block_time(update, context)


def price_command(update: Update, context: CallbackContext):
    """
    Get the current price in USD, EUR and CHF
    """
    price(update, context)


def halving_command(update: Update, context: CallbackContext):
    """
    Get the time until the next halving
    """
    halving(update, context)


def moscow_time_command(update: Update, context: CallbackContext):
    """
    Get the current moscow time (sat/USD, sat/EUR and sat/CHF)
    """
    moscow_time(update, context)


def sat_in_fiat_command(update: Update, context: CallbackContext):
    """
    Get the current EUR value of your sat amount
    """
    sat_in_fiat(update, context)

def episode_command(update: Update, context: CallbackContext):
    """
    Get the most recent podcast episode
    """
    episode(update, context)


def shoutout_command(update: Update, context: CallbackContext) -> int:
    """
    Returns a TallyCoin LN invoice for a specific amount that includes a memo
    """
    return shoutout(update, context)


def memo_command(update: Update, context: CallbackContext) -> int:
    """
    Returns a TallyCoin LN invoice for a specific amount that includes a memo
    """
    return memo(update, context)


def invoice_command(update: Update, context: CallbackContext) -> int:
    """
    Returns a TallyCoin LN invoice for a specific amount that includes a memo
    """
    return invoice(update, context)


def cancel_command(update: Update, context: CallbackContext) -> int:
    """
    Returns a TallyCoin LN invoice for a specific amount that includes a memo
    """
    return cancel(update, context)


def fortune_teller_command(update: Update, context: CallbackContext):
    """
    Sends the Hosp fortune_teller picture
    """
    fortune_teller(update, context)


def soundboard_command(update: Update, context: CallbackContext):
    """
    Sends back a markup of soundboard files
    """
    soundboard(update, context)


def run(bot_token: str):
    """
    Starts the bot
    """

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    setup_database()

    updater = Updater(token=bot_token)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start_command, run_async=True)
    taproot_handler = CommandHandler('taproot', taproot_command, run_async=True)
    fee_handler = CommandHandler('fee', fee_command, run_async=True)
    mempool_handler = CommandHandler('mempool', mempool_command, run_async=True)
    price_handler = CommandHandler('price', price_command, run_async=True)
    halving_handler = CommandHandler('halving', halving_command, run_async=True)
    sat_in_fiat_handler = CommandHandler('satinfiat', sat_in_fiat_command, run_async=True)
    block_time_handler = CommandHandler('block_time', block_time_command, run_async=True)
    moscow_time_handler = CommandHandler('moscow_time', moscow_time_command, run_async=True)
    fortune_teller_handler = CommandHandler('fortune_teller', fortune_teller_command, run_async=True)
    

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(taproot_handler)
    dispatcher.add_handler(fee_handler)
    dispatcher.add_handler(mempool_handler)
    dispatcher.add_handler(price_handler)
    dispatcher.add_handler(halving_handler)
    dispatcher.add_handler(sat_in_fiat_handler)
    dispatcher.add_handler(block_time_handler)
    dispatcher.add_handler(moscow_time_handler)
    dispatcher.add_handler(fortune_teller_handler)


    job_queue = dispatcher.job_queue

    if config.FEATURE_ATH:
        job_queue.run_repeating(price_update_ath, 10)

    if config.USE_WEBHOOK:
        updater.start_webhook(
            listen='0.0.0.0',
            port=config.WEBHOOK_PORT,
            webhook_url=f'https://{config.WEBHOOK_URL}:{config.WEBHOOK_PORT}/{bot_token}',
            url_path=bot_token,
            cert='cert.pem',
            key='private.key'
        )
        updater.idle()
    else:
        updater.start_polling()
