import types
from aiogram import Bot, executor, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from sql import DataBase
from config import TOKEN, USER_ID
from kbs import kb_client
from main import main
from aiogram.contrib.fsm_storage.memory import MemoryStorage

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot, storage=storage)


class Articul(StatesGroup):
    articul = State()

class Reit(StatesGroup):
    reit = State()


db = DataBase('data\statistica.db')



@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    await msg.answer('Привет', reply_markup=kb_client)


@dp.message_handler(Text(equals=['го']))
async def vivo_tovara(msg: types.Message):
    list = db.get_articul()
    if list != []:
        new_list = []
        await msg.answer('Собираю данные ...')
        for item in list:
            for i in item[0].split('\n'):

                articul = i.split(';')[0].split()[0]
                name = i.split(';')[-1]
                card = await main(articul,name)
                print(card)

                new_list.append(f'{card}\n')
        print(new_list)
        new_list = '\n'.join(new_list)
        await msg.answer(new_list,parse_mode='HTML')
        await msg.answer('Готово')
    else:
        await msg.answer('Добавте хотя бы один список ')

@dp.message_handler(Text(equals='список'))
async def Fsm(msg: types.Message):
    if msg.chat.id in USER_ID:
        db.del_articul()
        db.del_stat()
        await msg.answer('Введите список ')
        await Articul.articul.set()
    else:
        await msg.answer('У вас нет прав')


@dp.message_handler(state=Articul.articul)
async def name(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['articul'] = msg.text
        db.add_articul(data['articul'])
    await msg.answer('Данные добавлены')
    await state.finish()


@dp.message_handler(Text(equals='рейт'))
async def Fsm_reit(msg: types.Message):
    if msg.chat.id in USER_ID:
        await msg.answer('Введите новый рейтинг ')
        await Reit.reit.set()
    else:
        await msg.answer('У вас нет прав')

@dp.message_handler(state=Reit.reit)
async def name(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['reit'] = msg.text
        db.add_reit(data['reit'])
    await msg.answer('Рейтинг изменен')
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)