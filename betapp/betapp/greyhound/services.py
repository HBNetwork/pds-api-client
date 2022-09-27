import numpy as np
from django.db.models import Q, Avg, F
from .models import *
from .utils import remarks
from .utils.crawler import *

API_URL = 'https://greyhoundbet.racingpost.com/search/blocks.sd?'


def race_by_grade(races):
    """ Separa as corridas do dia em categorias """
    output = {"A": [], "D": [], "S": [], "HP": [], "OR": [], "ALL": []}
    for race in races:
        if "A" in race.grade:
            output['A'].append(race)
        elif "D" in race.grade:
            output['D'].append(race)
        elif "S" in race.grade:
            output['S'].append(race)
        elif "HP" in race.grade:
            output['HP'].append(race)
        elif "OR" in race.grade:
            output['OR'].append(race)

        output['ALL'].append(race)

    return output


def bends(race):
    output = {
        'bends': {},
        'maxbends': {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            'fin': 0
        }
    }
    for t in Trap.objects.filter(race=race):
        output['bends'][t.position] = calc_bends(t.dog, race.distance, 10)

    for i in output['bends']:
        if output['bends'][i]['bend1'] > output['maxbends'][1]:
            output['maxbends'][1] = output['bends'][i]['bend1']

        if output['bends'][i]['bend2'] > output['maxbends'][2]:
            output['maxbends'][2] = output['bends'][i]['bend2']

        if output['bends'][i]['bend3'] > output['maxbends'][3]:
            output['maxbends'][3] = output['bends'][i]['bend3']

        if output['bends'][i]['bend4'] > output['maxbends'][4]:
            output['maxbends'][4] = output['bends'][i]['bend4']

        if output['bends'][i]['fin'] > output['maxbends']['fin']:
            output['maxbends']['fin'] = output['bends'][i]['fin']

    for i in output['bends']:
        if output['maxbends'][1]:
            output['bends'][i]['bend1'] = 100 - round((output['bends'][i]['bend1'] * 100)/output['maxbends'][1], 2)
        if output['maxbends'][2]:
            output['bends'][i]['bend2'] = 100 - round((output['bends'][i]['bend2'] * 100)/output['maxbends'][2], 2)
        if output['maxbends'][3]:
            output['bends'][i]['bend3'] = 100 - round((output['bends'][i]['bend3'] * 100) / output['maxbends'][3], 2)
        if output['maxbends'][4]:
            output['bends'][i]['bend4'] = 100 - round((output['bends'][i]['bend4'] * 100) / output['maxbends'][4], 2)
        if output['maxbends']['fin']:
            output['bends'][i]['fin'] = 100 - round((output['bends'][i]['fin'] * 100) / output['maxbends']['fin'], 2)

    return output


def calc_bends(dog, distance, count):
    bends = {"bend1": 0,
             "bend2": 0,
             "bend3": 0,
             "bend4": 0,
             "fin": 0}

    for history in History.objects.filter(dog=dog, distance=distance).exclude(bends='').order_by('-date')[:count]:
        if bend := history.bends:
            bends['bend1'] += int(bend[0] or 0)
            if len(bend) > 1:
                bends['bend2'] += int(bend[1] or 0)
            if len(bend) > 2:
                bends['bend3'] += int(bend[2] or 0)
            if len(bend) > 3:
                bends['bend4'] += int(bend[3] or 0)
            bends['fin'] += int(history.placing)

    return bends

def direction(trap, distance, count):
    remarks = {
        'rls': 0,
        'mid': 0,
        'wide': 0,
    }

    for history in History.objects.filter(dog=trap.dog, distance=distance).order_by('-date')[:count]:
        if 'Rls' in history.remarks and 'Mid' in history.remarks:
            remarks['rls'] += 1
            remarks['mid'] += 1
        elif 'Rls' in history.remarks:
            remarks['rls'] += 1
        elif 'Mid' in history.remarks:
            remarks['mid'] += 1
        elif 'W' in history.remarks:
            remarks['wide'] += 1

    # Todos valores iguais, retorna center
    if all(value == remarks['rls'] for value in remarks.values()):
        return 'center'

    direction = max(remarks, key=remarks.get)
    if trap.position in [1, 2] and direction == 'rls':
        return 'left'
    elif trap.position in [1, 2] and direction in ['mid', 'wide']:
        return 'right'
    elif trap.position in [3, 4] and direction == 'rls':
        return 'left'
    elif trap.position in [3, 4] and direction == 'mid':
        return 'center'
    elif trap.position in [3, 4] and direction == 'right':
        return 'right'
    elif trap.position in [5, 6] and direction in ['rls', 'mid']:
        return 'left'
    elif trap.position in [5, 6] and direction == 'wide':
        return 'center'

    return None

def avb_comparative(race_id, a, b):
    """ Efetua o comparativo entre dois galgos """
    output = {
        'a': {},
        'b': {},
        'dif': {},
        'win': {},
        'alerts': [],
        'histories': {},
        'histories_grade': {},
        'histories_trap': {},
        'infos': {},
        'trap': {}
    }

    race = Race.objects.get(race_id=race_id)
    traps = Trap.objects.filter(Q(position=a) | Q(position=b), race=race)
    for trap in traps:
        output['histories'][str(trap.position)] = History.objects.filter(dog=trap.dog).order_by('-date')[:10]
        output['histories_grade'][str(trap.position)] = History.objects.filter(dog=trap.dog, grade=race.grade).order_by('-date')[:10]
        output['histories_trap'][str(trap.position)] = History.objects.filter(dog=trap.dog, trap=trap.position).order_by('-date')[:10]
        output['infos'][str(trap.position)] = Info.objects.get(dog=trap.dog, race=race)
        output['trap'][str(trap.position)] = trap

    # embate
    embate_message = embate(race, traps[0].dog, traps[1].dog)
    output['embate'] = embate_message

    # A
    output['a']['name'] = traps[0].dog.name
    output['a']['trap'] = traps[0].position
    output['a']['sex'] = traps[0].dog.gender
    output['a']['away'] = days_away(traps[0].dog, race)

    rating_a = rating(traps[0].dog, race)
    output['a']['rating'] = rating_a

    avg_pos_a = avg_pos(traps[0].dog, race)
    output['a']['avg_pos'] = avg_pos_a

    last_split_a = last_splits(traps[0].dog, race, 1)
    output['a']['last_split'] = last_split_a

    top_split_a = top_split(traps[0].dog, race)
    output['a']['topsplit'] = top_split_a

    avg_split_a = avg_split(traps[0].dog, race)
    output['a']['avg_split'] = avg_split_a

    last_time_a = last_times(traps[0].dog, race, 1)
    output['a']['last_time'] = 0
    if last_time_a:
        output['a']['last_time'] = last_time_a[0]

    avg_time_a = avg_time(traps[0].dog, race)
    output['a']['avg_time'] = avg_time_a

    avg_winner_time_a = calc_wintime(traps[0].dog, race)
    output['a']['avg_winner_time'] = avg_winner_time_a

    brt_a, brt_date_a = best_recent_time(traps[0].dog, race)
    output['a']['brt'] = brt_a
    output['a']['brt_date'] = brt_date_a

    topspeed_a = topspeed(traps[0].dog, race)
    output['a']['topspeed'] = topspeed_a

    avg_speed_a = avg_speed(traps[0].dog, race)
    output['a']['avg_speed'] = avg_speed_a

    trainer_a = trainer(traps[0].dog, race)
    output['a']['trainer'] = trainer_a

    points_a, grade_a = last_grade(traps[0].dog)
    output['a']['points'] = points_a
    output['a']['grade'] = grade_a

    output['a']['avg_recovery'] = round(avg_time_a - avg_split_a, 2) if avg_split_a else 0
    output['a']['recovery'] = last_recovery(traps[0].dog)

    remarks_points_a = calc_remarks(traps[0].dog)
    output['a']['remarks'] = remarks_points_a

    # B
    output['b']['name'] = traps[1].dog.name
    output['b']['trap'] = traps[1].position
    output['b']['sex'] = traps[1].dog.gender
    output['b']['away'] = days_away(traps[1].dog, race)

    rating_b = rating(traps[1].dog, race)
    output['b']['rating'] = rating_b

    avg_pos_b = avg_pos(traps[1].dog, race)
    output['b']['avg_pos'] = avg_pos_b

    last_split_b = last_splits(traps[1].dog, race, 1)
    output['b']['last_split'] = last_split_b

    top_split_b = top_split(traps[1].dog, race)
    output['b']['topsplit'] = top_split_b

    avg_split_b = avg_split(traps[1].dog, race)
    output['b']['avg_split'] = avg_split_b

    last_time_b = last_times(traps[1].dog, race, 1)
    output['b']['last_time'] = 0
    if last_time_b:
        output['b']['last_time'] = last_time_b[0]

    avg_time_b = avg_time(traps[1].dog, race)
    output['b']['avg_time'] = avg_time_b

    avg_winner_time_b = calc_wintime(traps[1].dog, race)
    output['b']['avg_winner_time'] = avg_winner_time_b

    brt_b, brt_date_b = best_recent_time(traps[1].dog, race)
    output['b']['brt'] = brt_b
    output['b']['brt_date'] = brt_date_b

    topspeed_b = topspeed(traps[1].dog, race)
    output['b']['topspeed'] = topspeed_b

    avg_speed_b = avg_speed(traps[1].dog, race)
    output['b']['avg_speed'] = avg_speed_b

    trainer_b = trainer(traps[1].dog, race)
    output['b']['trainer'] = trainer_b

    points_b, grade_b = last_grade(traps[1].dog)
    output['b']['points'] = points_b
    output['b']['grade'] = grade_b

    output['b']['avg_recovery'] = round(avg_time_b - avg_split_b, 2) if avg_split_b else 0
    output['b']['recovery'] = last_recovery(traps[1].dog)

    remarks_points_b = calc_remarks(traps[1].dog)
    output['b']['remarks'] = remarks_points_b

    # rating
    output['win']['rating'], output['dif']['rating'] = diff_max(rating_a, rating_b, traps[0].position, traps[1].position)

    # avg pos
    output['win']['avg_pos'], output['dif']['avg_pos'] = diff(
        avg_pos_a, avg_pos_b, traps[0].position, traps[1].position)

    # last split
    output['win']['last_split'], output['dif']['last_split'] = diff(
        last_split_a, last_split_b, traps[0].position, traps[1].position)

    # top split
    output['win']['topsplit'], output['dif']['topsplit'] = diff(
        top_split_a, top_split_b, traps[0].position, traps[1].position)

    # avg split
    output['win']['avg_split'], output['dif']['avg_split'] = diff(
        avg_split_a, avg_split_b, traps[0].position, traps[1].position)

    # last time
    output['win']['last_time'], output['dif']['last_time'] = diff(
        output['a']['last_time'], output['b']['last_time'], traps[0].position, traps[1].position)

    # avg time
    output['win']['avg_time'], output['dif']['avg_time'] = diff(
        avg_time_a, avg_time_b, traps[0].position, traps[1].position)

    # avg winner time
    output['win']['avg_winner_time'], output['dif']['avg_winner_time'] = diff(
        avg_winner_time_a, avg_winner_time_b, traps[0].position, traps[1].position)

    # brt
    output['win']['brt'], output['dif']['brt'] = diff(
        brt_a, brt_b, traps[0].position, traps[1].position)

    # topspeed
    output['win']['topspeed'], output['dif']['topspeed'] = diff_max(
        topspeed_a, topspeed_b, traps[0].position, traps[1].position)

    # avg speed
    output['win']['avg_speed'], output['dif']['avg_speed'] = diff_max(
        avg_speed_a, avg_speed_b, traps[0].position, traps[1].position)

    # trainer
    output['win']['trainer'], output['dif']['trainer'] = diff_max(
        trainer_a, trainer_b, traps[0].position, traps[1].position)

    # grade
    output['win']['grade'], output['dif']['grade'] = diff_max(
        points_a, points_b, traps[0].position, traps[1].position)

    # alerts
    output['alerts'] = alerts_avb(traps[0].dog, race.distance, a)
    output['alerts'] += alerts_avb(traps[1].dog, race.distance, b)

    # avg recovey
    output['win']['avg_recovery'], output['dif']['avg_recovery'] = diff(
        output['a']['avg_recovery'], output['b']['avg_recovery'], traps[0].position, traps[1].position)

    # points recovery
    rec_points_a = calc_points_recovery(output['a']['recovery'])
    rec_points_b = calc_points_recovery(output['b']['recovery'])
    output['win']['recovery'], output['dif']['recovery'] = diff_max(
        rec_points_a, rec_points_b, traps[0].position, traps[1].position)

    # calc remarks
    output['win']['remarks'], output['dif']['remarks'] = diff_max(
        remarks_points_a, remarks_points_b, traps[0].position, traps[1].position)

    points = {'a': 0, 'b': 0}
    for attr in output['win']:
        if output['win'][attr] == traps[0].position: 
            points['a'] += 1
        elif output['win'][attr] == traps[1].position:
            points['b'] += 1

    output['points'] = points

    return output


def calc_points_recovery(recovery):
    points = 0
    for data in recovery:
        if data == 'up':
            points += 2
        elif data == 'down':
            points -= 2
        else:
            points += 1

    return points


def calc_remarks(dog):
    sum_remarks = 0

    for history in History.objects.filter(dog=dog).order_by('-date')[:5]:
        list_remarks = history.remarks.split(',')
        for remark in list_remarks:
            if remark in remarks.remarks.keys():
                sum_remarks += remarks.remarks[remark]

    return sum_remarks


def calc_remarks_trap(dog, race):
    points = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0}
    loops = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0}

    for history in History.objects.filter(dog=dog, duration__gt=0, trap__gt=0, distance=race.distance).order_by('-date'):
        list_remarks = history.remarks.split(',')
        for remark in list_remarks:
            if remark in remarks.remarks.keys():
                points[str(history.trap)] += remarks.remarks[remark]
                loops[str(history.trap)] += 1

    for key in points:
        if loops[key] > 0:
            points[key] = round(points[key] / loops[key], 2)

    return points


def diff(value_a, value_b, position_a, position_b):
    """ Retorna o menor valor entre dois valores """
    if not value_a or not value_b:
        return 101, 0

    if value_a < value_b:
        return position_a, round((value_b - value_a), 2)
    elif value_a > value_b:
        return position_b, round((value_a - value_b), 2)
    else:
        return 100, 0


def diff_max(value_a, value_b, position_a, position_b):
    """ Retorna o maior valor entre 2 valores """
    # Cod 100 - Equal
    # Cod 101 - No image
    if not value_a or not value_b:
        return 101, 0

    if value_a > value_b:
        return position_a, round((value_a - value_b), 2)
    elif value_a < value_b:
        return position_b, round((value_b - value_a), 2)
    else:
        return 100, 0


def avb_graphic(race_id, a, b):
    output = {
        a: {},
        b: {}
    }
    race = Race.objects.get(race_id=race_id)
    traps = Trap.objects.filter(Q(position=a) | Q(position=b), race=race)

    for trap in traps:
        output[trap.position]['name'] = trap.dog.name
        output[trap.position]['times'] = last_times(trap.dog, race, 10)
        output[trap.position]['splits'] = last_splits(trap.dog, race, 10)

    return output

def rating(dog, race):
    info = Info.objects.filter(dog=dog, race=race).first()
    return info.rating

def avg_pos(dog, race):
    """ Retorna a média de posição """
    history = History.objects.filter(dog=dog, distance=race.distance, grade__in=filter_grade(race.grade)).aggregate(avg_pos=Avg('placing'))
    return round(history['avg_pos'], 2) if history['avg_pos'] else 0


def top_split(dog, race):
    """ Retorna o melhor split do galgo """
    if history := History.objects.filter(
        dog=dog,
        race__track__track_id=race.track.track_id,
        distance=race.distance,
        grade__in=filter_grade(race.grade),
        split__gt=0,
    ).values_list('split', flat=True):
        history = min(remove_outlier(list(map(float, history))))
        return history

    return 0


def avg_split(dog, race):
    """ Retorna a média de split do galgo """
    if history := History.objects.filter(
        dog=dog,
        race__track__track_id=race.track.track_id,
        distance=race.distance,
        grade__in=filter_grade(race.grade),
        split__gt=0,
    ).values_list('split', flat=True):
        history = remove_outlier(list(map(float, history)))
        return round((sum(history) / len(history)), 2)

    return 0


def avg_time(dog, race):
    """ Retorna a média de tempo do galgo """
    if history := History.objects.filter(
        dog=dog,
        distance=race.distance,
        grade__in=filter_grade(race.grade),
        duration__gt=0,
    ).values_list('duration', flat=True):
        history = remove_outlier(list(map(float, history)))
        return round((sum(history) / len(history)), 2)

    return 0


def last_times(dog, race, count):
    """ Retorna os últimos tempo do galgo """
    history = History.objects.filter(dog=dog, distance=race.distance, grade__in=filter_grade(
        race.grade), duration__gt=0).order_by('-date').values_list('duration', flat=True)[:count]

    if not history:
        history = History.objects.filter(dog=dog, distance=race.distance, duration__gt=0).order_by('-date').first()
        return [float(history.duration)] if history else [0]
    return list(map(float, history))


def last_splits(dog, race, count):
    """ Retorna uma lista com a quantidade espcifica dos ultimos splits """
    if (
        history := History.objects.filter(
            dog=dog,
            race__track__track_id=race.track.track_id,
            distance=race.distance,
            grade__in=filter_grade(race.grade),
            split__gt=0,
        )
        .order_by('-date')
        .values_list('split', flat=True)
    ):
        if count > 1:
            return remove_outlier(list(map(float, history)))[:count]
        elif count == 1:
            return list(map(float, history))[0]

    return 0


def days_away(dog, race):
    info = Info.objects.get(dog=dog, race=race)
    return info.day_away


def best_recent_time(dog, race):
    info = Info.objects.get(dog=dog, race=race)
    return float(info.best_real_time or 0), info.best_real_time_date


def topspeed(dog, race):
    info = Info.objects.get(dog=dog, race=race)
    return info.top_speed


def forecast(dog, race):
    info = Info.objects.get(dog=dog, race=race)
    return float(info.forecast) if info.forecast else 3


def avg_speed(dog, race):
    races = last_times(dog, race, 1000)
    total_races = len(races)
    if not total_races or (total_races == 1 and races[0] == 0):
        return 0
    total_time = sum(races)
    avg_time = total_time/total_races
    speed = (race.distance/1000)/(avg_time/3600)
    return round(speed, 2)


def trainer(dog, race):
    dog_info = Info.objects.get(dog=dog, race=race)
    dogs = Dog.objects.filter(info__trainer__name=dog_info.trainer.name).distinct()
    races = Race.objects.filter(info__trainer__name=dog_info.trainer.name).distinct()
    count = History.objects.filter(dog__in=dogs, race__in=races, placing=1).count()

    return count


def track_stats(track_id, distance):
    stats = TrackStats.objects.get(track_id=track_id, distance=distance)
    return {
        'traps': [
            stats.trap1,
            stats.trap2,
            stats.trap3,
            stats.trap4,
            stats.trap5,
            stats.trap6,
        ],
        'sex': [stats.female, stats.male],
        'avg_weight': stats.avg_weight,
    }


def avg_time_in_trap(dog, distance):
    times = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0}
    loops = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0}

    history = History.objects.filter(
        dog=dog, duration__gt=0, trap__gt=0, distance=distance).all()

    for history in history:
        times[str(history.trap)] += history.duration
        loops[str(history.trap)] += 1

    for key in times:
        if loops[key] > 0:
            times[key] = round(times[key] / loops[key], 2)

    return times


def alerts_avb(dog, distance, trap):
    alert = []

    # Verificando o tempo do dog na trap
    avg_time = avg_time_in_trap(dog, distance)
    max_key = max(avg_time, key=avg_time.get)

    min_key = None
    min_value = 9999
    for key, value in avg_time.items():
        if value and value < min_value:
            min_key = key
            min_value = value

    if max_key == str(trap) and min_key != max_key:
        tmp = {"type": "alert alert-danger alert-dismissible",
               "msg": f"O galgo da trap {trap} possui a pior média de tempo correndo nessa trap. Sua melhor média de tempo é correndo na trap {min_key}"}
        alert.append(tmp)

    if min_key == str(trap) and min_key != max_key:
        tmp = {"type": "alert alert-success",
               "msg": f"O galgo da trap {trap} possui a melhor média de tempo correndo nessa trap. Sua pior média de tempo é correndo na trap {max_key}"}
        alert.append(tmp)

    return alert


def last_grade(dog):
    grade_a = ['A12', 'A11', 'A10', 'A9', 'A8',
               'A7', 'A6', 'A5', 'A4', 'A3', 'A2', 'A1']
    grade_d = ['D5', 'D4', 'D3', 'D2', 'D1']
    grade_s = ['S10', 'S9', 'S8', 'S7', 'S6', 'S5', 'S4', 'S3', 'S2', 'S1']
    grade_t = ['T5', 'T4', 'T3', 'T2', 'T1']

    grades = grade_a + grade_d + grade_s + grade_t
    history = History.objects.filter(dog=dog).order_by('-date').all()[:5]

    output = ""
    points = 0
    for data in history:

        if data.grade in grades:
            output += f"{data.grade} - "

            if data.grade != "A0" and "A" in data.grade:
                points += grade_a.index(data.grade)
            elif "D" in data.grade:
                points += grade_d.index(data.grade)
            elif data.grade != "HS1" and "S" in data.grade:
                points += grade_s.index(data.grade)
            elif data.grade != "IT" and data.grade != "NT" and "T" in data.grade:
                points += grade_t.index(data.grade)
            else:
                points += 1

    return points, output[:-3]


def last_recovery(dog):
    """ Retorna a recuperação do galgo nas últimas corridas """
    history = History.objects.filter(dog=dog).order_by('-date').all()[:12]

    return [history.recovery() for history in history]


def filter_grade(grade):
    grade_a = ['A11', 'A10', 'A9', 'A8', 'A7',
               'A6', 'A5', 'A4', 'A3', 'A2', 'A1']
    grade_b = ['B7', 'B6', 'B5', 'B4', 'B3', 'B2', 'B1']
    grade_d = ['D4', 'D3', 'D2', 'D1']
    grade_hp = ['HP']
    grade_or = ['OR']
    grade_s = ['S8', 'S7', 'S6', 'S5', 'S4', 'S3', 'S2', 'S1']
    if "A" in grade:
        return grade_a
    elif "B" in grade:
        return grade_b
    elif "D" in grade:
        return grade_d
    elif "S" in grade:
        return grade_s
    elif "HP" in grade:
        return grade_hp
    elif "OR" in grade:
        return grade_or
    else:
        grade_t = ['T4', 'T3', 'T2', 'T1']

        return grade_a + grade_t

def calc_wintime(dog, race):
    history = History.objects.filter(dog=dog, distance=race.distance, grade__in=filter_grade(race.grade), duration__gt=0, winner_time__gt=0).order_by('-date')[:10]
    sum_wintime = 0
    loop = 0
    for hist in history:
        if hist.going != "N":
            sum_wintime += float(hist.winner_time) + (int(hist.going) / 100)
        else:
            sum_wintime += float(hist.winner_time)

        loop += 1

    return round(sum_wintime/loop, 2) if loop else 0

def remove_outlier(values):
    fator = 2.0  # 1.5 é o fator de multiplicacao
    # retorna o terceiro e primeiro quartil
    q75, q25 = np.percentile(values, [75, 25])
    iqr = q75 - q25  # calcula o iqr(interquartile range)

    # calcula o valor minimo para aplicar no filtro
    lowpass = q25 - (iqr * fator)
    # calcula o valor maximo para aplicar no filtro
    highpass = q75 + (iqr * fator)

    # descobre onde estao os valores menores que o valor minimo
    outliers = np.argwhere(values < lowpass)
    values = np.delete(values, outliers)  # deleta esses valores

    # descobre onde estao os valores maiores que o valor maximo
    outliers = np.argwhere(values > highpass)
    values = np.delete(values, outliers)  # deleta esses valores

    return list(values)


def get_greyhound_history(dog):
    URL = f'{API_URL}dog_id={str(dog.dog_id)}&blocks=search-dog-header%2Csearch-dog-details'
    data = fetch_data(URL)

    for hist_json in data['search-dog-details']['forms']:
        race_id = hist_json['rInstId'] or int(
            hist_json['raceTime'].replace("-", "").split(" ")[0]
            + hist_json['trackId']
            + hist_json['winnersTimeS'].replace(".", "")
        )

        grade = hist_json['rGradeCde'] or hist_json['trialFlag']
        track = Track.objects.filter(
            track_id=int(hist_json['trackId'])).first()
        if not track:
            track_name = filter_name_abbr(hist_json['trackShortName'])
            track = Track.objects.create(track_id=int(hist_json['trackId']),
                                         name=track_name,
                                         country="GB")

        race = Race.objects.filter(race_id=race_id).first()
        if not race:
            race = Race.objects.create(
                track=track,
                race_id=race_id,
                distance=int(only_digits(hist_json['distMetre'])),
                grade=grade,
                date=to_datetime(hist_json['raceTime'])
            )

        history, created = History.objects.get_or_create(
            history_id=hist_json['rInstId'] or None,
            dog=dog,
            race=race,
            distance=int(only_digits(hist_json['distMetre'])),
            grade=grade,
            date=to_datetime(hist_json['raceTime']),
            winner_time=hist_json['winnersTimeS'],
            going=str(hist_json['goingType']),
            trap=int(only_digits(hist_json['trapNum'])),
            split=float(only_digits(hist_json['secTimeS'])),
            bends=hist_json['bndPos'].replace("-", ""),
            placing=int(only_digits(hist_json['rOutcomeId'])),
            odds_frctn_numer=int(only_digits(hist_json['oddsFrctnNumer'])),
            odds_frctn_denom=int(only_digits(hist_json['oddsFrctnDenom'])),
            duration=float(only_digits(hist_json['calcRTimeS'])),
            remarks=hist_json['closeUpCmnt'],
            weight=float(only_digits(hist_json['weight']))
        )

        if not created:
            break

def filter_dogs(data):
    goal = data.pop('goal')
    trap_position = data.pop('position', None)
    gender = data.pop('gender', None)
    track = data.pop('track', None)
    grade = data.pop('grade', None)
    distance = data.pop('distance', None)
    result = data.pop('result', None)
    rating = data.pop('rating', None)

    exclude_tipdetails = data.pop('exclude_tipdetails', None)
    exclude_racingpost = data.pop('exclude_racingpost', None)
    exclude_sportinglife = data.pop('exclude_sportinglife', None)
    exclude_timeform = data.pop('exclude_timeform', None)

    exclude_query = Q()
    if exclude_tipdetails:
        exclude_query |= Q(tipdetails__in=data.pop('tipdetails', []))
    if exclude_racingpost:
        exclude_query |= Q(racingpost__in=data.pop('racingpost', []))
    if exclude_sportinglife:
        exclude_query |= Q(sportinglife__in=data.pop('sportinglife', []))
    if exclude_timeform:
        exclude_query |= Q(timeform__in=data.pop('timeform', []))

    query = {f'{k}__in':v for k, v in data.items()}
    trap_position and query.setdefault('trap__position__in', trap_position)
    gender and query.setdefault('trap__dog__gender__in', gender)
    track and query.setdefault('trap__race__track__in', track)
    grade and query.setdefault('trap__race__grade__in', grade)
    distance and query.setdefault('trap__race__distance__in', distance)
    result and query.setdefault('trap__race__result__placing__in', result)

    if result:
        query.setdefault('trap__race__result__trap', F('trap'))

    if rating:
        rating = rating.split(":")
        query.setdefault('trap__race__info__rating__gte', int(rating[0]))
        query.setdefault('trap__race__info__rating__lte', int(rating[1]))
        query.setdefault('trap__race__info__dog', F('trap__dog'))


    scores = Score.objects \
        .prefetch_related('trap', 'trap__race', 'trap__dog') \
        .filter(**query).exclude(exclude_query).order_by('trap__race__date')

    output = {'list': [], 'results': {}}
    green = 0
    red = 0
    wait = 0
    for data in scores:
        result =  verify_result(data.trap, goal,  data.trap.race.result())

        if 'green' in result:
            green += 1
        elif 'red' in result:
            red += 1
        elif 'wait' in result:
            wait += 1

        tmp = {
            "race": data.trap.race,
            "dog": data.trap.dog,
            'info': Info.objects.get(race=data.trap.race, dog=data.trap.dog),
            "trap": data.trap,
            "status": result,
            "score": data
        }
        output['list'].append(tmp)

    output['results'] = {
        'green': green,
        'red': red,
        'percent': round(green/(green + red), 2) * 100 if (green+red) else 0,
        'wait': wait
    }

    return output

def last_weight(dog):
    if hist := History.objects.filter(dog=dog).order_by('-date').first():
        return hist.weight
    return 0

def transform_in_rank(data, reverse=False):
        points = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0}

        i = 6
        lastValue = None
        for key in sorted(data, key=data.get, reverse=reverse):
            if lastValue and lastValue != data[key]:
                i -= 1

            lastValue = data[key]
            points[key] = i

        for point in sorted(points, key=points.get, reverse=reverse):
            points[str(point)] = (7 - points[str(point)])

        return points

def verify_result(trap, objetive, result):
    if not result:
        return '<i title="Sem Resultado" class="fas fa-spinner wait"></i>'
    if objetive == "back":
        if trap.position == int(result[0]):
            return '<i title="Green" class="fas fa-check-circle green"></i>'
    elif objetive == "backplaced":
        if trap.position in [int(result[0]), int(result[1])]:
            return '<i title="Green" class="fas fa-check-circle green"></i>'
    elif objetive == "lay":
        if trap.position != int(result[0]):
            return '<i title="Green" class="fas fa-check-circle green"></i>'
    elif objetive == "layplaced":
        if trap.position not in [int(result[0]), int(result[1])]:
            return '<i title="Green" class="fas fa-check-circle green"></i>'
    elif objetive == "top3":
        if len(result) >= 3 and trap.position in [
            int(result[0]),
            int(result[1]),
            int(result[2]),
        ]:
            return '<i title="Green" class="fas fa-check-circle green"></i>'

    return '<i title="Red" class="fas fa-times red"></i>'

def embate(race, dog_a, dog_b):
    hist1 = History.objects.filter(dog=dog_a).exclude(grade__in=['T1', 'T2', 'T3', 'T4', 'T5']).order_by('-date')
    hist2 = History.objects.filter(dog=dog_b).exclude(grade__in=['T1', 'T2', 'T3', 'T4', 'T5']).order_by('-date')
    messages = []
    for h1 in hist1:
        for h2 in hist2:
            if h1.race.date == h2.race.date:
                if h1.placing < h2.placing:
                    msg = f'{h1.dog.name} correndo pela trap {h1.trap} enfrentou {h2.dog.name} correndo pela trap {h2.trap} no dia {h1.date.strftime("%d-%m-%Y")} e ganhou o AvB.<br> {h1.dog.name} chegou na posição {h1.placing} com o tempo de {h1.duration} e {h2.dog.name} chegou em {h2.placing} com o tempo de {h2.duration}'
                else:
                    msg = f'{h2.dog.name} correndo pela trap {h2.trap} enfrentou {h1.dog.name} correndo pela trap {h1.trap} no dia {h2.date.strftime("%d-%m-%Y")} e ganhou o AvB.<br> {h2.dog.name} chegou na posição {h2.placing} com o tempo de {h2.duration} e {h1.dog.name} chegou em {h1.placing} com o tempo de {h1.duration}'

                if h1.race.video and h1.race.video.url:
                    msg += f' <br><a href="javascript:void(0)" data-toggle="modal" data-target="#modalVideo" data-msg="{h1.dog.name} na trap {h1.trap} e {h2.dog.name} na trap {h2.trap}" data-video="{h1.race.video.url}"><img width="22" src="/static/images/player.png"> Assistir Corrida</a>'
                messages.append({ "race": h1.race, "message": msg})
    return messages
