from dateutil import tz
from django.db import models
from django.utils.timezone import datetime


class TrackRaceQuerySet(models.QuerySet):
    def today(self):
        today = datetime.now(tz=tz.gettz('Europe/London'))
        start = today.replace(hour=0, minute=0)
        end = today.replace(hour=23, minute=59)
        return self.filter(race__date__range=[start, end]).order_by('name').distinct()


class TrackRaceManager(models.Manager):
    def get_queryset(self):
        return TrackRaceQuerySet(self.model, using=self._db)

    def today(self):
        return self.get_queryset().today()

