from django.core.management.base import BaseCommand

from betapp.greyhound.models import *
from betapp.greyhound.services import get_greyhound_history
from betapp.greyhound.utils.crawler import *


class Command(BaseCommand):
    help = 'Mineração das Corridas'

    def handle(self, *args, **options):
        self.london = tz.gettz('Europe/London')
        self.today = datetime.now(tz=self.london)
        self.today_to_string = self.today.strftime("%Y-%m-%d")
        self.import_races()
        self.import_dogs_on_race()
        self.import_history()

    def import_races(self):
        URL = f"https://greyhoundbet.racingpost.com/meeting/blocks.sd?r_date={self.today_to_string}&view=time&blocks=header%2Clist"


        data = fetch_data(URL)

        total_races = sum(race['racesCount'] for race in data['list']['items'])
        count = 0
        for track_json in data['list']['items']:
            track, _ = Track.objects.get_or_create(track_id=int(track_json['track_id']), 
                                            name=track_json['track'],
                                            country=track_json['races'][0]['country'])

            for race_json in track_json['races']:
                race = Race.objects.filter(race_id=race_json['raceId'])

                if not race.exists():
                    race = Race.objects.create(
                        track=track,
                        race_id=race_json['raceId'],
                        distance=int(re.findall(r'\d+', race_json['distance'])[0]),
                        grade=race_json['raceGrade'],
                        date=to_datetime(race_json['raceDate']), post_pick=''
                    )

                count += 1
                stats = round((count/total_races) * 100, 2)
                print(f"{stats}% races imported", end='\r')

    def import_dogs_on_race(self):
        lower = datetime(self.today.year, self.today.month, self.today.day, tzinfo=self.london)
        greater = datetime(self.today.year, self.today.month, self.today.day, 23, 59, tzinfo=self.london)

        races = Race.objects.filter(date__lte=greater, date__gte=lower)

        total_dogs = len(races) * 6
        count = 0
        for race in races:
            URL = f"https://greyhoundbet.racingpost.com/card/blocks.sd?race_id={str(race.race_id)}&r_date={self.today_to_string}&tab=form&blocks=card-header%2Ccard-pager%2Ccard-tabs%2Ccard-title%2Cform"


            data = fetch_data(URL)

            for dog_json in data['form']['dogs']:

                dog = Dog.objects.filter(dog_id=dog_json['dogId']).first()
                if not dog:
                    dog = Dog.objects.create(name=dog_json['dogName'], dog_id=dog_json['dogId'],
                                                   color=dog_json['dogColor'], gender=dog_json['dogSex'],
                                                   birth=to_datetime(dog_json['dateOfBirth'], '%d%b%y'),
                                                   sire=dog_json['sire'], dam=dog_json['dam'])
                elif dog.name != dog_json['dogName']: # dog mudou de nome
                        dog.name = dog_json['dogName']
                        dog.save()

                if (
                    not dog_json['forecast']
                    or '/' not in dog_json['forecast']
                    or 'N/O' in dog_json['forecast']
                ):
                    dog_json['forecast'] = '0'

                handicap = None
                if race.grade == 'HP':
                    handicap = dog_json['handicapMetre'].replace('(', '').replace(')', '').replace('R', '')
                    if handicap == 'Scr':
                        handicap = 0

                exists_info = Info.objects.filter(dog=dog, race=race)

                if not exists_info:
                    exists_trainer = Trainer.objects.filter(name=dog_json['trainerName'])

                    trainer = (
                        exists_trainer[0]
                        if exists_trainer
                        else Trainer.objects.create(
                            name=dog_json['trainerName'],
                            location=dog_json['trainerLocation'],
                        )
                    )

                    season = dog_json['dateOfSeason'].replace('(', '').replace(')', '')
                    season_type = None
                    season_date = None
                    if season:
                        if ' ' in season:
                            season = season.split(' ')
                            season_type = season[0].strip()
                            season_date = datetime.strptime(season[1].strip(), '%d%b%y')
                        else:
                            season_type = season

                    info = Info.objects.create(
                        dog=dog, race=race, top_speed=dog_json['topSpeed'] ,
                        best_real_time=dog_json['brt'] or None, trainer=trainer,
                        forecast=eval(dog_json['forecast']),
                        best_real_time_grade=dog_json['bestTimeGrade'],
                        best_real_time_date=to_datetime(dog_json['bestTimeGradeDate'], '%d%b%y'),
                        comments=dog_json['forecastComment'],
                        reserve=False,
                        date_of_season=season_date,
                        type_of_season=season_type,
                        handicap=handicap
                    )

                trap, _ = Trap.objects.get_or_create(dog=dog, race=race, position=dog_json['trapNum'])
                race.post_pick = data['card-title']['postPick']
                race.save()

                count += 1
                stats = round((count/total_dogs) * 100, 2)
                print(f"{stats}% dogs imported...", end='\r')

    def import_history(self):
        lower = datetime(self.today.year, self.today.month, self.today.day, tzinfo=self.london)
        greater = datetime(self.today.year, self.today.month, self.today.day, 23, 59, tzinfo=self.london)

        races = Race.objects.filter(date__lte=greater, date__gte=lower)
        traps = Trap.objects.filter(race__in=races)

        total_traps = len(traps)
        for count, trap_info in enumerate(traps, start=1):
            get_greyhound_history(trap_info.dog)

            stats = round((count/total_traps) * 100, 2)
            print(f"{stats}% history of race imported", end='\r')
