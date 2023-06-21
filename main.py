from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import osteo_bot.config
from user_bot_admin import UserBotAdmin
from calendar_admin import CalendarAdmin
from db_admin import DBADMIN

bot = Bot(osteo_bot.config.token)
dp = Dispatcher(bot)

user_bot_admin = UserBotAdmin()
calendar_admin = CalendarAdmin()
db_admin = DBADMIN()


@dp.message_handler(commands=['start'])
async def start_handler(msg: types.Message):
    db_admin.add_chatid(username=msg.from_user.username, chatid=msg.from_user.id)
    await bot.send_message(chat_id=msg.chat.id, text='1. Щоб записатися на прийом, натисніть на "Записатися на прийом 👨".\n'
                                                     '2. Ви можете переглянути всі ваші записи, натиснувши на "Мої записи 📅".\n'
                                                     '3. Щоб скасувати прийом, натисніть на "Мої записи 📅" ➞ "скасувати прийом ❌" під відповідним записом.\n'
                                                     '4. Відповіді на найпоширеніші запитання ви можете побачити, натиснувши на "FAQ ❓"\n'
                                                     '5. Щоб переглянути це повідомлення ще раз, надішліть "/start" у чат.',
                           reply_markup=user_bot_admin.main_kb())


@dp.message_handler(content_types=['text'])
async def text_handler(msg: types.Message):
    if msg.text == 'FAQ ❓':
        await bot.send_message(chat_id=msg.chat.id, text='*FAQ*')

    elif msg.text == 'Мої записи 📅':
        if not calendar_admin.show_sessions(name=msg.from_user.username).items():
            await bot.send_message(chat_id=msg.chat.id, text='У вас немає жодного запису.')
        else:
            for s_d, s_t in calendar_admin.show_sessions(name=msg.from_user.username).items():
                for t in s_t:
                    delete_kb = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text='Скасувати сеанс ❌',
                                                                                           callback_data=f'del {s_d} {t} {msg.from_user.username}'))
                    await bot.send_message(chat_id=msg.chat.id, text=f'{s_d}: {t}', reply_markup=delete_kb)

    elif msg.text == 'Записатися на сеанс 👨':
        await bot.send_message(chat_id=msg.chat.id, text='Виберіть дату та час сеансу 🔀',
                               reply_markup=user_bot_admin.calendar_kb(username=msg.from_user.username))


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('day'))
async def calendar_keyboard_callback_data_handler(call: types.CallbackQuery):
    day, username = int(call.data.split()[1]), call.data.split()[2]
    await bot.send_message(chat_id=call.message.chat.id, text=f'Ви вибрали {day} число. Тепер виберіть час сеансу 🔀',
                           reply_markup=user_bot_admin.time_schedule_kb(day=day, username=username))


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('hour'))
async def time_schedule_keyboard_callback_data_handler(call: types.CallbackQuery):
    day, hour, username = int(call.data.split()[1]), call.data.split()[2], call.data.split()[3]
    calendar_admin.schedule_session(name=username, day=day, hour=hour)
    await bot.send_message(chat_id=call.message.chat.id, text='Сеанс додано ✅')
    await bot.send_message(chat_id=730344077, text=f'@{username} додав сеанс на {day} число на {hour} 🤑')


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('del'))
async def delete_session_keyboard_callback_data_handler(call: types.CallbackQuery):
    day, hour, username = int(call.data.split()[1].split('.')[0]), call.data.split()[2], call.data.split()[3]
    calendar_admin.cancel_session(day=day, hour=hour)
    await bot.send_message(chat_id=call.message.chat.id, text='Сеанс скасовано ✅')
    await bot.send_message(chat_id=730344077, text=f'@{username} скасував сеанс на {day} число на {hour} 😢')
    # 941572438


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
