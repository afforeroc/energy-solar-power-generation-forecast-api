import datetime
import pytz
from tzlocal import get_localzone


def obtain_time_zone_name():
    local_timezone = get_localzone()
    time_zone_name = local_timezone.key
    return time_zone_name


def obtain_utc_offset(time_zone_name):
    timezone = pytz.timezone(time_zone_name)
    aware_datetime = timezone.localize(datetime.datetime.now())
    utc_offset = aware_datetime.utcoffset()
    return utc_offset


def obtain_utc_offset_time(utc_offset):
    total_seconds = utc_offset.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    if utc_offset.days < 0:
        sign = -1
    else:
        sign = 1
    return sign, hours, minutes


if __name__ == "__main__":
    time_zone_name = obtain_time_zone_name()
    print(f"Your time zone is {time_zone_name}")
    utc_offset = obtain_utc_offset(time_zone_name)
    sign, hours, minutes = obtain_utc_offset_time(utc_offset)
    print(f"UTC Time offset is {sign*hours}:{abs(minutes):02}")
