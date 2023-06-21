from googleapiclient.discovery import build
from google.oauth2 import service_account

from db_admin import DBADMIN

from datetime import date

db_admin = DBADMIN()


class CalendarAdmin:
    def __init__(self):
        path = 'user_bot/osteobot-45b1ca77ee21.json'
        scopes = ['https://www.googleapis.com/auth/calendar']
        creds = service_account.Credentials.from_service_account_file(path, scopes=scopes)
        self.service = build('calendar', 'v3', credentials=creds)

    def get_data(self):
        sessions = self.service.events().list(
            calendarId='59fe109a1f2589a4454c6b5b7b49f3195e689f8626837cc068b8e2117c92ef22@group.calendar.google.com',
            singleEvents=True,
            orderBy='startTime'
        ).execute().get('items', [])

        return [(session['summary'], session['start'].get('dateTime'), session['id']) for session in sessions]

    def schedule_session(self, name: str, day: int, hour: str):
        curr_year = date.today().year
        s_month = date.today().month if date.today().day <= day else date.today().month + 1
        s_month = ('0' + str(s_month)) if s_month <= 9 else str(s_month)

        self.service.events().insert(
            calendarId='59fe109a1f2589a4454c6b5b7b49f3195e689f8626837cc068b8e2117c92ef22@group.calendar.google.com',
            body={
                'summary': name,
                'start': {
                    'dateTime': f'{curr_year}-{s_month}-{day}T{hour}:00+03:00',
                    'timeZone': 'Europe/Kiev'
                },
                'end': {
                    'dateTime': f'{curr_year}-{s_month}-{day}T{(int(hour[:2]) + 1) if hour[0] != "0" and hour[1] != 9 else ("0" + int(hour[:2]) + 1)}:00:00+03:00',
                    'timeZone': 'Europe/Kiev'
                }
            }
        ).execute()

    def reschedule_session(self, name: str, old_day: int, old_hour: str, new_day: int, new_hour: str):
        self.cancel_session(day=old_day, hour=old_hour)
        self.schedule_session(name=name, day=new_day, hour=new_hour)

    def cancel_session(self, day: int, hour: str):
        event_id = ''
        for s in self.get_data():
            s_day, s_hour = int(s[1][8:10]), s[1][11:16]
            if day == s_day and hour == s_hour:
                event_id = s[2]
                break

        request = self.service.events().delete(
            **{'calendarId': '59fe109a1f2589a4454c6b5b7b49f3195e689f8626837cc068b8e2117c92ef22@group.calendar.google.com', 'eventId': event_id}
        )
        request.execute()

    def show_sessions(self, name: str) -> dict:
        your_sessions = {}

        sessions = self.get_data()
        for s in sessions:
            year, month, day, hour = int(s[1][:4]), int(s[1][5:7]), int(s[1][8:10]), s[1][11:16]
            if s[0] == name and year >= date.today().year and (month == date.today().month and day >= date.today().day) or (month == date.today().month + 1):
                try:
                    your_sessions[f'{day}.{month}'].append(hour)
                except KeyError:
                    your_sessions[f'{day}.{month}'] = [hour]

        return your_sessions

    def show_sessions_rooted(self, range_) -> dict or str:
        all_sessions = {}

        sessions = self.get_data()
        for s in sessions:
            if s[0] != 'blocked':
                name, year, month, day, hour = s[0], int(s[1][:4]), int(s[1][5:7]), int(s[1][8:10]), s[1][11:16]
                if year >= date.today().year and (month == date.today().month and day >= date.today().day) or (month == date.today().month + 1):
                    try:
                        all_sessions[f'{day}.{month}'].append((hour, name))
                    except KeyError:
                        all_sessions[f'{day}.{month}'] = [(hour, name)]

        try:
            if range_ == 'today':
                return {f'{int(date.today().day)}.{int(date.today().month)}': all_sessions[f'{int(date.today().day)}.{int(date.today().month)}']}

            elif range_ == 'week':
                week_sessions = {}
                for s in all_sessions.keys():
                    if int(s[:s.index('.')]) > (int(date.today().day) + 7) % 30:
                        break
                    week_sessions[s] = all_sessions[s]
                return week_sessions

            else:
                return all_sessions

        except KeyError:
            return 'None'

    def available_time(self) -> dict:
        schedule = self.__create_schedule()

        sessions = self.get_data()
        for s in sessions:
            year, month, day, hour = int(s[1][:4]), int(s[1][5:7]), int(s[1][8:10]), s[1][11:16]
            if year >= date.today().year and month >= date.today().month and day >= date.today().day + 1:
                try:
                    schedule[day].remove(hour)
                except ValueError:
                    pass

        return schedule

    @staticmethod
    def __create_schedule() -> dict:
        days_in_months = {1: 31, 2: 28 if date.today().year % 4 != 0 else 29, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
        curr_day, curr_month = date.today().day, date.today().month

        keys = []
        for d in range(curr_day + 1, days_in_months[curr_month] + 1):
            day_date = date(date.today().year, curr_month, d)
            if date.weekday(day_date) != 3:
                keys.append(d)

        for d in range(1, 29 - (days_in_months[curr_month] - curr_day)):
            day_date = date(date.today().year + 1 if curr_month == 12 else date.today().year, curr_month + 1, d)
            if date.weekday(day_date) != 3:
                keys.append(d)

        values = [['10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00'] for _ in range(30)]

        return dict(zip(keys, values))
