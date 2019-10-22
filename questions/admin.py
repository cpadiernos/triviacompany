from django.contrib import admin
from .models import Game

class GameAdmin(admin.ModelAdmin):
    model = Game
    list_display = ('date', 'question_set', 'worksheet', 'notes')
    
admin.site.register(Game, GameAdmin)
