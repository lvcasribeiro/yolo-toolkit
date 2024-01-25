# Imports:
from datetime import datetime, date

# Captures the current date and time:
def datetime_capture():
    current_date = date.today().strftime('%d-%m-%Y')

    current_hour = datetime.now().hour
    current_minute = datetime.now().minute
    current_second = datetime.now().second

    current_datetime = f'{current_hour}-{current_minute}-{current_second}_{current_date}'
    
    return current_datetime
