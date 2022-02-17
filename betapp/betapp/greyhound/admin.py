from django.contrib import admin

from .models import *


@admin.register(Dog)
class DogAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ('name', 'color', 'gender', 'birth', 'sire', 'dam', 'age')


@admin.register(Info)
class InfoAdmin(admin.ModelAdmin):
    raw_id_fields = ['dog', 'race', 'trainer']
    search_fields = ['dog__name', 'dog__dog_id', 'race__race_id']
    list_display = ('dog', 'top_speed', 'best_real_time', 'forecast',
                    'best_real_time_grade', 'best_real_time_date',
                    'comments', 'type_of_season', 'date_of_season', 'reserve', 'handicap')


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    search_fields = ['dog__name', 'dog__dog_id', 'race__race_id']
    list_display = ('history_id', 'trap', 'dog', 'split', 'distance',
                    'grade', 'bends', 'placing', 'remarks', 'duration', 'going')


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    search_fields = ('id', 'race_id', 'date', 'track__name')
    list_display = ('id', 'date', 'track', 'grade', 'distance', 'post_pick',
                    'tipdetails')


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    search_fields = ['race__race_id']
    list_display = ('race', 'trap', 'placing')


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')


@admin.register(Trap)
class TrapAdmin(admin.ModelAdmin):
    raw_id_fields = ['dog', 'race']
    search_fields = ['dog__name', 'race__race_id']
    list_display = ('dog', 'race', 'position')


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    search_fields = ['track_id', 'name', 'country']
    list_display = ('track_id', 'name', 'country')


@admin.register(TrackStats)
class TrackStatsAdmin(admin.ModelAdmin):
    search_fields = ['track_id']
    list_display = ('track_id', 'distance')


@admin.register(Remark)
class RemarkAdmin(admin.ModelAdmin):
    list_display = ('remark', 'description', 'color')

