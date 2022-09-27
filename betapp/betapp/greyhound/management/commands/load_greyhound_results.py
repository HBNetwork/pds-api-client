from dateutil import tz
from datetime import datetime
from django.core.management.base import BaseCommand

from betapp.greyhound.models import *
from betapp.greyhound.services import get_greyhound_history
from betapp.greyhound.utils.crawler import *

class Command(BaseCommand):
    help = 'Mineração dos Resultados'

    def handle(self, *args, **options):
        self.london = tz.gettz('Europe/London')
        self.today = datetime.now(tz=self.london)
        self.today_to_string = self.today.strftime("%Y-%m-%d")
        self.import_results()
        self.stdout.write(self.style.SUCCESS('Successfully'))

    def import_results(self):
        lower = datetime(self.today.year, self.today.month, self.today.day, tzinfo=self.london)

        races = Race.objects.filter(date__lte=self.today, date__gte=lower)

        for race in races:
            result = Result.objects.filter(race=race)
            if not result.exists() or len(result) <= 4:
                url = f"https://greyhoundbet.racingpost.com/results/blocks.sd?race_id={str(race.race_id)}&track_id={str(race.track.track_id)}&r_date={self.today_to_string}&blocks=meetingHeader%2Cresults-meeting-pager%2Clist"

                data = fetch_data(url)


                if "errorCode" in data['list']:
                    continue

                pks = [int(x) for x in data['list']['track']['results'].keys()]

                if race.race_id in pks:
                    for result in data['list']['track']['results'][str(race.race_id)]:
                        dog = Dog.objects.filter(dog_id=int(result['dogId'])).first()
                        trap = Trap.objects.filter(race=race, dog=dog).first()

                        if bool(int(result['isReserved'])) and not trap:

                            if not dog:
                                dog = Dog.objects.create(
                                    name=result['name'], dog_id=result['dogId'],
                                    color=result['dogColor'], gender=result['dogSex'],
                                    birth=to_datetime(result['dogDateOfBirth']),
                                    sire=result['dogSire'], dam=result['dogDam'])

                            info = Info.objects.filter(dog=dog, race=race)

                            if not info:
                                trainer = Trainer.objects.filter(name=result['trainer']).first()

                                if not trainer:
                                    trainer = Trainer.objects.create(name=result['trainer'], location='')

                                Info.objects.create(dog=dog, race=race, trainer=trainer, reserve=True)

                            # Atualizando a trap
                            trap = Trap.objects.filter(race=race, position=result['trap']).first()
                            trap.dog = dog
                            trap.save()

                            # Atualizar o historico do dog
                            get_greyhound_history(dog)

                        if result['position'] != 'N':
                            Result.objects.get_or_create(race=race, trap=trap, placing=result['position'])