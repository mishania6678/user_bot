from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from calendar_admin import CalendarAdmin


class UserBotAdmin:
    def __init__(self):
        pass

    @staticmethod
    def main_kb() -> ReplyKeyboardMarkup:
        kb = ReplyKeyboardMarkup(row_width=2)
        kb.add(
            KeyboardButton(text='FAQ ❓'),
            KeyboardButton(text='Мої записи 📅'),
            KeyboardButton(text='Записатися на сеанс 👨')
        )

        return kb

    def calendar_kb(self, username: str) -> InlineKeyboardMarkup:
        schedule = CalendarAdmin().available_time()

        days = []
        for d in schedule.keys():
            if schedule[d]:
                days.append(d)

        kb = InlineKeyboardMarkup(row_width=5)
        kb.add(*[InlineKeyboardButton(text=str(d), callback_data=f'day {d} {username}') for d in days])

        return kb

    def time_schedule_kb(self, day: int, username: str) -> InlineKeyboardMarkup:
        hours = CalendarAdmin().available_time()[day]

        kb = InlineKeyboardMarkup(row_width=5)
        kb.add(*[InlineKeyboardButton(text=h, callback_data=f'hour {day} {h} {username}') for h in hours])

        return kb
