from datetime import date

from dateutil.relativedelta import relativedelta
from django.db import models
from django.db.models import Manager

from .choices import *
from .managers import TrackRaceManager


class Dog(models.Model):
    name = models.CharField(max_length=255)
    dog_id = models.IntegerField(unique=True)
    color = models.CharField(max_length=255)
    gender = models.CharField(max_length=255)
    birth = models.DateField(blank=True, null=True)
    sire = models.CharField(max_length=255, default='Not informed', blank=True,
            null=True)
    dam = models.CharField(max_length=255)

    def age(self):
        today = date.today()
        age = relativedelta(today, self.birth)
        old = ''
        old += f'{str(age.years)} anos ' if age.years > 1 else f'{str(age.years)} ano '
        if age.months and age.months > 1:
            old += f'{str(age.months)} meses'
        else:
            old += f'{str(age.months)} mês'

        return old

    def age_days(self):
        today = date.today()
        age = relativedelta(today, self.birth)
        return (age.years * 365) + (age.months * 30) + age.days

    def current_weight(self):
        return self.history_set.last().weight if self.history_set.last() else 0

    def __str__(self):
        return f'{self.name}'


class Info(models.Model):
    dog = models.ForeignKey('Dog', on_delete=models.CASCADE)
    race = models.ForeignKey('Race', on_delete=models.CASCADE)
    trainer = models.ForeignKey('Trainer', on_delete=models.CASCADE)
    top_speed = models.IntegerField(default=0)
    best_real_time = models.DecimalField(max_digits=5, decimal_places=2, blank=True,
            null=True)
    forecast = models.DecimalField(max_digits=5, decimal_places=2, blank=True,
            null=True)
    best_real_time_grade = models.CharField(max_length=4, null=True)
    best_real_time_date = models.DateField(null=True)
    comments = models.CharField(max_length=255, null=True)
    reserve = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)
    date_of_season = models.DateField(null=True)
    type_of_season = models.CharField(max_length=25, blank=True, null=True)
    handicap = models.CharField(max_length=10, blank=True, null=True)

    def day_away(self):
        today = today = date.today()
        if hist := History.objects.filter(dog=self.dog).order_by('-date').first():
            return (today - hist.date.date()).days - 1
        return None


class History(models.Model):
    history_id = models.IntegerField(null=True)
    dog = models.ForeignKey('Dog', on_delete=models.CASCADE)
    race = models.ForeignKey('Race', on_delete=models.CASCADE)
    distance = models.IntegerField()
    grade = models.CharField(max_length=4)
    date = models.DateTimeField()
    winner_time = models.DecimalField(max_digits=4, decimal_places=2, blank=True,
            null=True)
    going = models.CharField(max_length=4, blank=True, null=True)
    trap = models.IntegerField(blank=True, null=True)
    split = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    bends = models.CharField(max_length=4, blank=True, null=True)
    placing = models.IntegerField(blank=True, null=True)
    odds_frctn_numer = models.IntegerField(blank=True, null=True)
    odds_frctn_denom = models.IntegerField(blank=True, null=True)
    duration = models.DecimalField(max_digits=5, decimal_places=2, blank=True,
            null=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    weight = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True,
            default=0)

    def recovery(self):
        if self.bends:
            if (int(self.bends[0]) - self.placing) < 0:
                return 'down'
            elif (int(self.bends[0]) - self.placing) > 0:
                return 'up'
            else:
                return 'hold'

    def split_remarks(self):
        output = []
        for data in  self.remarks.split(','):
            remark = Remark.objects.filter(remark=data).first()
            if remark:
                tmp = {
                        'remark': remark.remark,
                        'description': remark.description,
                        'color_text': "tooltip_text_green" if remark.color == 'green' else 'tooltip_text_grey' if remark.color == 'grey' else 'tooltip_text_red',
                        'color_bg': "tooltip_green" if remark.color == 'green' else 'tooltip_grey' if remark.color == 'grey' else 'tooltip_red'
                        }
            else:
                tmp = {
                        'remark': data,
                        'description': None,
                        }
            output.append(tmp)

        return output


class Remark(models.Model):
    remark = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=50)
    color = models.CharField(max_length=7)


class Race(models.Model):
    track = models.ForeignKey('Track', on_delete=models.CASCADE)
    race_id = models.BigIntegerField(unique=True)
    distance = models.IntegerField()
    grade = models.CharField(max_length=255)
    date = models.DateTimeField()
    post_pick = models.CharField(max_length=255, blank=True, null=True)
    tipdetails = models.CharField(max_length=255, blank=True, null=True)
    sportinglife = models.CharField(max_length=255, blank=True, null=True)
    timeform = models.CharField(max_length=255, blank=True, null=True)
    tipdetails_remarks = models.CharField(max_length=255, blank=True, null=True)
    video = models.FileField(upload_to='replays', null=True, blank=True)

    def __str__(self):
        return f'{self.date} - {self.track.name} - {self.grade}'

    def post_pick_traps(self):
        return self.post_pick[:5].split('-') if self.post_pick else []

    def sportinglife_tips(self):
        return self.sportinglife[:5].split('-') if self.sportinglife else []

    def timeform_tips(self):
        return self.timeform[:5].split('-') if self.timeform else []

    def tips(self):
        return self.tipdetails.split('-') if self.tipdetails else []

    def result(self):
        return self.result_set.values_list('trap__position', flat=True).order_by('placing')


class Result(models.Model):
    race = models.ForeignKey('Race', on_delete=models.CASCADE)
    trap = models.ForeignKey('Trap', on_delete=models.CASCADE)
    placing = models.CharField(max_length=2)


class Trainer(models.Model):
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255, blank=True, null=True)


class Track(models.Model):
    track_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    objects = Manager()
    races = TrackRaceManager()

    def __str__(self):
        return f'{self.name}'


class TrackStats(models.Model):
    track_id = models.IntegerField()
    distance = models.IntegerField()
    trap1 = models.IntegerField(default=0)
    trap2 = models.IntegerField(default=0)
    trap3 = models.IntegerField(default=0)
    trap4 = models.IntegerField(default=0)
    trap5 = models.IntegerField(default=0)
    trap6 = models.IntegerField(default=0)
    female = models.IntegerField(default=0)
    male = models.IntegerField(default=0)
    avg_weight = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    def __str__(self):
        track = Track.objects.get(track_id=self.track_id)
        return f'{track.name} - {self.distance}'


class Trap(models.Model):
    dog = models.ForeignKey('Dog', on_delete=models.CASCADE)
    race = models.ForeignKey('Race', on_delete=models.CASCADE, related_name='traps')
    position = models.IntegerField()

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f'{self.position} -  {self.dog.name}'

