from datetime import datetime
from dateutil import tz
import json
import re
import time
from urllib.request import urlopen


def fetch_data(URL):
    for i in range(50):
        try:
            with urlopen(URL) as url:
                return json.loads(url.read().decode())
        except:
            print(f'#{i}', URL)
            time.sleep(10)


def only_digits(data):
    return match.group() if (match := re.search(r'(\d+(\.\d+)?)', data)) else 0


def to_datetime(date, mask='%Y-%m-%d %H:%M'):
    if not date:
        return None

    london = tz.gettz('Europe/London')
    date = datetime.strptime(date, mask).replace(tzinfo=london)
    return date


def filter_name_abbr(name):
    names = {
        "Clnml": "Clonmel",
        "CPark": "Central Park",
        "Cryfd": "Crayford",
        "Dndlk": "Dundalk",
        "Donc": "Doncaster",
        "Ennis": "Enniscorthy",
        "Hnlow": "Henlow",
        "Kinsly": "Kinsley",
        "Kilky": "Kilkenny",
        "Limrk": "Limerick",
        "Longfd": "Longford",
        "Monmr": "Monmore",
        "Mulgr": "Mullingar",
        "Nwbrdg": "Newbridge",
        "Newc": "Newcastle",
        "Notts": "Nottingham",
        "Pbrgh": "Peterborough",
        "PerB": "Perry Barr",
        "Pelaw": "Pelaw Grange",
        "Romfd": "Romford",
        "Sland": "Sunderland",
        "Sheff": "Sheffield",
        "ShelPk": "Shelbourne Park",
        "Swndn": "Swindon",
        "Towc": "Towcester",
        "Thurl": "Thurles",
        "Trlee": "Tralee",
        "Youghl": "Youghal",
        "Yrmth": "Yarmouth",
        "Wtrfd": "Waterford"
    }

    return names.get(name, name)
