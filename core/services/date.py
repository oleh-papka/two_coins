import calendar
import datetime

from django.utils import timezone


class DateService:
    @staticmethod
    def get_date_start_end():
        now = timezone.now()

        first_day = datetime.date(now.year, now.month, 1)
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        last_day = datetime.date(now.year, now.month, days_in_month)

        return first_day, last_day

    @staticmethod
    def parse_date(value):
        if isinstance(value, datetime.date):
            return value
        if value:
            try:
                return datetime.datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                return None
        return None