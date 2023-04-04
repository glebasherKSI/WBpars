from aiogram.types import KeyboardButton,ReplyKeyboardMarkup

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton('список')
b2 = KeyboardButton('рейт')
b3 = KeyboardButton('го')

kb_client.add(b3).add(b1).add(b2)