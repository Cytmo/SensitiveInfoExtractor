from datetime import datetime
from datetime import timedelta
'''
    将时间戳转换为日期格式

    内存泄漏是否处理：是
'''

def convert_format_time(time_days):
    start_date = datetime(1970, 1, 1)
    target_date = start_date + timedelta(days=time_days)
    result_data = target_date.strftime('%Y-%m-%d')
    del start_date
    del time_days
    return result_data