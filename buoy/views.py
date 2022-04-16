from django.shortcuts import render
import requests
import datetime
from dateutil import tz


def get_buoy_data(url, name):
    r = requests.get(url)

    if r.status_code == 404:
        if datetime.datetime.now().month in [11, 12, 1, 2, 3, 4]:
            data = "Current conditions are not available (probably because it is still winter in the UP!)"
        else:
            data = "Current conditions are not available"
        return {"data": data}

    x = 0
    data = []
    for line in r.iter_lines(decode_unicode=True):
        data.append(line.split())
        x += 1
        if x == 4:
            break

    utc_tz = tz.gettz("UTC")
    et_tz = tz.gettz("America/Detroit")
    time_utc = datetime.datetime.strptime(
        f"{data[2][1]}/{data[2][2]}/{data[2][0]} {data[2][3]}:{data[2][4]}",
        "%m/%d/%Y %H:%M",
    )
    time_utc.replace(tzinfo=utc_tz)
    time_eastern = time_utc.astimezone(et_tz)

    info = {
        f"{name}_time": f"{time_eastern:%m/%d/%Y %H:%M} ET",
        f"{name}_wind_direction": data[2][5],
        f"{name}_wind_speed": round(float(data[2][6]) / 0.44704, 2),
        f"{name}_wind_gusts": round(float(data[2][7]) / 0.44704, 2),
        f"{name}_wave_height": round(float(data[2][8]) * 3.2808, 2),
        f"{name}_air_temp": round(float(data[2][13]) * 1.8 + 32, 2),
    }

    return info


def home_page_view(request):
    info = {}

    north_data = get_buoy_data(
        "https://www.ndbc.noaa.gov/data/realtime2/45023.txt", "north"
    )
    south_data = get_buoy_data(
        "https://www.ndbc.noaa.gov/data/realtime2/45025.txt", "south"
    )
    info.update(north_data)
    info.update(south_data)

    return render(request, "main.html", context=info)

