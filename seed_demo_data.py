import os
import django
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from gamification.models import (
    Achievement, 
    UserAchievement, 
    UserGamificationProfile, 
    ExperienceEvent, 
    Challenge, 
    ChallengeParticipation
)
from skills.models import Skill, UserSkillProgress
from exercises.models import Exercise
from submissions.models import Submission

User = get_user_model()

def seed_all():
    print("=== 1. Creando o actualizando Logro 'Atrévete a Aprender' ===")
    ach_dare, _ = Achievement.objects.update_or_create(
        stable_id="ACH_START_JOURNEY",
        defaults={
            "title": "Atrévete a Aprender",
            "description": "Completaste el registro y resolviste tu evaluación diagnóstica. El primer paso hacia la maestría es atreverse a aprender.",
            "image_url": "https://img.icons8.com/color/96/000000/launch.png"
        }
    )
    print(f"Logro listo: {ach_dare.title} ({ach_dare.stable_id})")

    print("\n=== 2. Corrigiendo congruencia de Grafo vs Dashboard en usuarios existentes ===")
    # Para cualquier usuario, si mastery_percentage == 0, is_initialized debe ser False
    UserSkillProgress.objects.filter(mastery_percentage=0).update(is_initialized=False)
    
    # Específico para camanrofo34:
    user_caman34 = User.objects.filter(username='camanrofo34').first()
    if user_caman34:
        # Asegurar que solo Arreglos y Strings y Recursión Básica estén activas con 20%
        UserSkillProgress.objects.filter(user=user_caman34).update(is_initialized=False, mastery_percentage=0.0)
        
        arr_skill = Skill.objects.filter(name__icontains="Arreglos y Strings").first()
        if arr_skill:
            usp, _ = UserSkillProgress.objects.get_or_create(user=user_caman34, skill=arr_skill)
            usp.mastery_percentage = 20.0
            usp.is_initialized = True
            usp.save()

        rec_skill = Skill.objects.filter(name__icontains="Recursión Básica").first()
        if rec_skill:
            usp, _ = UserSkillProgress.objects.get_or_create(user=user_caman34, skill=rec_skill)
            usp.mastery_percentage = 20.0
            usp.is_initialized = True
            usp.save()
            
        # Darle el logro de atreverse a aprender por haber completado el diagnóstico
        UserAchievement.objects.get_or_create(
            user=user_caman34,
            achievement=ach_dare,
            defaults={"reason": "Completaste el registro y evaluación diagnóstica inicial."}
        )
        print("Usuario camanrofo34 ajustado con éxito (2 habilidades activas al 20%, congruencia total).")

    # También para camanrofo si existe:
    user_caman = User.objects.filter(username='camanrofo').first()
    if user_caman:
        UserAchievement.objects.get_or_create(
            user=user_caman,
            achievement=ach_dare,
            defaults={"reason": "Completaste el registro y evaluación diagnóstica inicial."}
        )

    print("\n=== 3. Creando usuarios universitarios: CallMeDrift y TheWeregh ===")
    
    # 1. Diego Alejandro Suarez Mendoza (CallMeDrift)
    diego, created_d = User.objects.update_or_create(
        username="CallMeDrift",
        defaults={
            "full_name": "Diego Alejandro Suarez Mendoza",
            "email": "callmedrift@upb.edu.co",
            "university": "Universidad Pontificia Bolivariana",
            "current_semester": 8,
            "faculty": "Ingeniería de Sistemas e Informática",
            "role": User.Role.STUDENT,
            "is_student": True,
        }
    )
    if created_d:
        diego.set_password("Password123!")
        diego.save()
    
    # 2. Luis Alfredo Fuentes Romero (TheWeregh)
    luis, created_l = User.objects.update_or_create(
        username="TheWeregh",
        defaults={
            "full_name": "Luis Alfredo Fuentes Romero",
            "email": "theweregh@upb.edu.co",
            "university": "Universidad Pontificia Bolivariana",
            "current_semester": 8,
            "faculty": "Ingeniería de Sistemas e Informática",
            "role": User.Role.STUDENT,
            "is_student": True,
        }
    )
    if created_l:
        luis.set_password("Password123!")
        luis.save()
        
    print(f"Usuario Diego: @{diego.username} ({diego.full_name})")
    print(f"Usuario Luis: @{luis.username} ({luis.full_name})")

    print("\n=== 4. Asignando ejercicios resueltos (dificultad 100) y perfiles gamificados ===")
    ex_001 = Exercise.objects.filter(stable_id="EX_001").first() # Suma de Dos (100)
    ex_002 = Exercise.objects.filter(stable_id="EX_002").first() # Palíndromo Válido (100)
    ex_003 = Exercise.objects.filter(stable_id="EX_003").first() # Anagramas (100)
    ex_004 = Exercise.objects.filter(stable_id="EX_004").first() # Frecuencia de Elementos (100)
    ex_010 = Exercise.objects.filter(stable_id="EX_010").first() # Conteo de Bits (100)
    ex_011 = Exercise.objects.filter(stable_id="EX_011").first() # Búsqueda Rápida (100)

    # Submissions para Diego (CallMeDrift): EX_001, EX_002, EX_003, EX_010
    diego_exercises = [e for e in [ex_001, ex_002, ex_003, ex_010] if e]
    for ex in diego_exercises:
        sub, _ = Submission.objects.get_or_create(
            author=diego,
            exercise=ex,
            defaults={
                "source_code": "# Solución óptima por CallMeDrift\ndef solve(): pass",
                "language": "python",
                "state": Submission.State.COMPLETED,
                "verdict": Submission.Verdict.ACCEPTED,
                "time_used_ms": 45,
                "memory_used_kb": 14200
            }
        )

    # Perfil gamificado Diego: Nivel 3, 280 XP, 3 días racha
    prof_diego, _ = UserGamificationProfile.objects.update_or_create(
        user=diego,
        defaults={
            "points": 280,
            "level": 3,
            "current_streak": 3,
            "highest_streak": 4,
            "last_action_date": timezone.now().date()
        }
    )

    # Insignias para Diego
    for ach_stable in ["ACH_START_JOURNEY", "ACH_FIRST_BLOOD", "ACH_FAST_MIND", "ACH_GLADIATOR"]:
        ach_obj = Achievement.objects.filter(stable_id=ach_stable).first()
        if ach_obj:
            UserAchievement.objects.get_or_create(
                user=diego,
                achievement=ach_obj,
                defaults={"reason": "Otorgado por desempeño académico y retos completados."}
            )

    # Progreso de habilidades para Diego
    for skill_name, mastery in [("Arreglos y Strings", 60.0), ("Hash Tables / Maps", 45.0), ("Manipulación de Bits", 40.0)]:
        s = Skill.objects.filter(name__icontains=skill_name.split()[0]).first()
        if s:
            usp, _ = UserSkillProgress.objects.get_or_create(user=diego, skill=s)
            usp.mastery_percentage = mastery
            usp.is_initialized = True
            usp.save()

    # Submissions para Luis (TheWeregh): EX_001, EX_004, EX_011
    luis_exercises = [e for e in [ex_001, ex_004, ex_011] if e]
    for ex in luis_exercises:
        sub, _ = Submission.objects.get_or_create(
            author=luis,
            exercise=ex,
            defaults={
                "source_code": "# Solución óptima por TheWeregh\ndef solve(): pass",
                "language": "python",
                "state": Submission.State.COMPLETED,
                "verdict": Submission.Verdict.ACCEPTED,
                "time_used_ms": 52,
                "memory_used_kb": 13900
            }
        )

    # Perfil gamificado Luis: Nivel 2, 190 XP, 2 días racha
    prof_luis, _ = UserGamificationProfile.objects.update_or_create(
        user=luis,
        defaults={
            "points": 190,
            "level": 2,
            "current_streak": 2,
            "highest_streak": 3,
            "last_action_date": timezone.now().date()
        }
    )

    # Insignias para Luis
    for ach_stable in ["ACH_START_JOURNEY", "ACH_FIRST_BLOOD", "ACH_FAST_MIND"]:
        ach_obj = Achievement.objects.filter(stable_id=ach_stable).first()
        if ach_obj:
            UserAchievement.objects.get_or_create(
                user=luis,
                achievement=ach_obj,
                defaults={"reason": "Otorgado por desempeño académico inicial."}
            )

    # Progreso de habilidades para Luis
    for skill_name, mastery in [("Arreglos y Strings", 45.0), ("Búsqueda Rápida", 40.0)]:
        s = Skill.objects.filter(name__icontains=skill_name.split()[0]).first()
        if s:
            usp, _ = UserSkillProgress.objects.get_or_create(user=luis, skill=s)
            usp.mastery_percentage = mastery
            usp.is_initialized = True
            usp.save()

    print("\n=== 5. Configurando Retos Semanales (Semana Actual y Próxima Semana) ===")
    now = timezone.now()
    
    # Challenge 1: Semana Actual (En Vivo)
    # Lunes de esta semana a Domingo de esta semana
    start_this_week = now - timedelta(days=2) # e.g. 2 días atrás
    end_this_week = now + timedelta(days=4, hours=18) # Termina en ~4 días

    ch1, _ = Challenge.objects.update_or_create(
        stable_id="weekly-001",
        defaults={
            "title": "Reto Semanal #1: Fundamentos Algorítmicos y Arreglos",
            "description": "Compite en vivo contra tus compañeros de ingeniería. Resuelve los 3 problemas seleccionados de arreglos, búsqueda y condicionales antes del cierre semanal para ganar puntos extra en el ranking y la insignia de 'Gladiador'.",
            "start_date": start_this_week,
            "end_date": end_this_week
        }
    )
    ch1_exercises = [e for e in [ex_001, ex_002, ex_003] if e]
    ch1.exercises.set(ch1_exercises)

    # Participantes en Challenge 1
    ChallengeParticipation.objects.update_or_create(
        challenge=ch1,
        user=diego,
        defaults={"score": 200, "joined_at": start_this_week + timedelta(hours=3)}
    )
    ChallengeParticipation.objects.update_or_create(
        challenge=ch1,
        user=luis,
        defaults={"score": 100, "joined_at": start_this_week + timedelta(hours=5)}
    )

    # Challenge 2: Próxima Semana (Próximamente)
    start_next_week = end_this_week + timedelta(hours=6)
    end_next_week = start_next_week + timedelta(days=7)

    ch2, _ = Challenge.objects.update_or_create(
        stable_id="weekly-002",
        defaults={
            "title": "Reto Semanal #2: Estructuras Dinámicas y Recursión",
            "description": "El próximo reto pondrá a prueba tu capacidad para manipular secuencias, pilas y recursión básica. ¡Pre-inscríbete desde ya para apartar tu cupo en la arena de competencia!",
            "start_date": start_next_week,
            "end_date": end_next_week
        }
    )
    ch2_exercises = [e for e in [ex_004, ex_010, ex_011] if e]
    ch2.exercises.set(ch2_exercises)

    # Pre-inscritos en Challenge 2
    ChallengeParticipation.objects.update_or_create(
        challenge=ch2,
        user=diego,
        defaults={"score": 0, "joined_at": now - timedelta(hours=4)}
    )
    ChallengeParticipation.objects.update_or_create(
        challenge=ch2,
        user=luis,
        defaults={"score": 0, "joined_at": now - timedelta(hours=2)}
    )

    print(f"Reto 1 listo: {ch1.title} ({ch1.exercises.count()} ejercicios, {ch1.participations.count()} inscritos)")
    print(f"Reto 2 listo: {ch2.title} ({ch2.exercises.count()} ejercicios, {ch2.participations.count()} inscritos)")
    print("\n¡Sembrado de datos para demostración completado con éxito!")

if __name__ == '__main__':
    seed_all()

