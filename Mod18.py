import telebot
import requests
import json

token_telegram = "YOUR TELEGRAM BOT TOKEN"
token_site = "YOUR SITE TOKEN"

bot = telebot.TeleBot(token_telegram)
keys = {
    'биткоин': 'BTC',
    'эфириум': 'ETH',
    'доллар': 'USD',
}


class ConvertionException(Exception):
    pass


class CryptoConverter:
    @staticmethod
    def convert(quote: str, base: str, amount: str):
        if quote == base:
            raise ConvertionException(f'Невозможно перевести одинаковые валюты {base}.')

        try:
            quote_ticker = keys[quote]
            base_ticker = keys[base]
        except KeyError:
            raise ConvertionException(f'Не удалось обработать валюту {quote}.')

        try:
            amount = float(amount)
        except ValueError:
            raise ConvertionException(f'Не удалось обработать количество {amount}.')

        try:
            r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={quote_ticker}&tsyms={base_ticker}&token_site={token_site}')
            total_base = json.loads(r.content)[keys[base]]
        except:
            raise ConvertionException(f"Не удалось сделать запрос на сайте.")

        return total_base * amount


@bot.message_handler(commands=['start','help'])
def help(message: telebot.types.Message):
    text = 'Чтобы начать работу, введите команду боту в следующем формате:' \
           '\n <имя валюты> <в какую валюту перевестию> <в качестве переводимой валюты>' \
           '\nУвидить список всех доступных валют: /values'
    bot.reply_to(message, text)


@bot.message_handler(commands=['values'])
def values (message: telebot.types.Message):
    text = 'Доступные валюты:'
    for key in keys:
        text += f"\n {key} - {keys[key]}"
    bot.reply_to(message, text)


@bot.message_handler(content_types=['text'])
def convert (message: telebot.types.Message):
    values = [str(i).lower() for i in message.text.split()]

    if len(values) !=3:
        raise ConvertionException('Слишком много параметров')

    quote, base, amount = values
    total_base = CryptoConverter.convert(quote, base, amount)

    text = f'Цена {amount} {quote} в {base} - {total_base}'
    bot.send_message(message.chat.id, text)


bot.polling(none_stop=True)
