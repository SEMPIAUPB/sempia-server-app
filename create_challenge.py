import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from gamification.models import Challenge
from exercises.models import Exercise

def run():
    now = timezone.now()
    # Create an active challenge (started 1 day ago, ends in 6 days)
    challenge, created = Challenge.objects.get_or_create(
        stable_id="weekly-001",
        defaults={
            "title": "Reto Semanal #1: Fundamentos Algorítmicos",
            "description": "Demuestra tu destreza con los arreglos, ciclos y condicionales básicos. Resuelve estos 3 ejercicios sin errores de ejecución para ganar 500 puntos de reputación y la insignia de 'Pionero'.",
            "start_date": now - timedelta(days=1),
            "end_date": now + timedelta(days=6)
        }
    )
    
    if not created:
        challenge.title = "Reto Semanal #1: Fundamentos Algorítmicos"
        challenge.description = "Demuestra tu destreza con los arreglos, ciclos y condicionales básicos. Resuelve estos 3 ejercicios sin errores de ejecución para ganar 500 puntos de reputación y la insignia de 'Pionero'."
        challenge.start_date = now - timedelta(days=1)
        challenge.end_date = now + timedelta(days=6)
        challenge.save()

    # Get some random exercises
    exercises = Exercise.objects.filter(status='PUBLISHED')[:3]
    challenge.exercises.set(exercises)

    # Create an upcoming challenge
    upcoming_challenge, created_up = Challenge.objects.get_or_create(
        stable_id="weekly-002",
        defaults={
            "title": "Reto Semanal #2: Maestría en Estructuras de Datos",
            "description": "El próximo reto pondrá a prueba tu capacidad para manejar listas, pilas y colas. ¡Prepárate para optimizar al máximo tus algoritmos!",
            "start_date": now + timedelta(days=7),
            "end_date": now + timedelta(days=14)
        }
    )
    
    if not created_up:
        upcoming_challenge.title = "Reto Semanal #2: Maestría en Estructuras de Datos"
        upcoming_challenge.description = "El próximo reto pondrá a prueba tu capacidad para manejar listas, pilas y colas. ¡Prepárate para optimizar al máximo tus algoritmos!"
        upcoming_challenge.start_date = now + timedelta(days=7)
        upcoming_challenge.end_date = now + timedelta(days=14)
        upcoming_challenge.save()

    exercises_up = Exercise.objects.filter(status='PUBLISHED')[3:6]
    if not exercises_up:
        exercises_up = exercises
    upcoming_challenge.exercises.set(exercises_up)
    
    print(f"Challenge 1: {challenge.title} with {challenge.exercises.count()} exercises.")
    print(f"Challenge 2: {upcoming_challenge.title} with {upcoming_challenge.exercises.count()} exercises.")

if __name__ == '__main__':
    run()
