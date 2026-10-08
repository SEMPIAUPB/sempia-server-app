import os
import django
import sys

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from gamification.models import Achievement

achievements_data = [
    {
        "stable_id": "ACH_FIRST_BLOOD",
        "title": "Primer Paso",
        "description": "El viaje de mil millas comienza con un solo paso. Resolviste tu primer problema en la plataforma.",
        "image_url": "https://img.icons8.com/color/96/000000/baby-footprints.png"
    },
    {
        "stable_id": "ACH_FAST_MIND",
        "title": "Mente Veloz",
        "description": "Primera solución Aceptada (AC) sin ningún error previo.",
        "image_url": "https://img.icons8.com/color/96/000000/flash-on.png"
    },
    {
        "stable_id": "ACH_GRAPH_KING",
        "title": "Rey de los Grafos",
        "description": "Dominio de las conexiones. Has resuelto 5 problemas relacionados con la teoría de grafos.",
        "image_url": "https://img.icons8.com/color/96/000000/network.png"
    },
    {
        "stable_id": "ACH_STREAK_3",
        "title": "Maratón Inicial",
        "description": "Mantuviste una racha de 3 días consecutivos resolviendo problemas.",
        "image_url": "https://img.icons8.com/color/96/000000/fire-element.png"
    },
    {
        "stable_id": "ACH_PERSISTENT",
        "title": "Cazador de Errores",
        "description": "La persistencia es clave. Recibiste 5 veredictos incorrectos antes de obtener un AC en el mismo problema.",
        "image_url": "https://img.icons8.com/color/96/000000/bug.png"
    },
    {
        "stable_id": "ACH_DATA_EXPERT",
        "title": "Experto en Estructuras",
        "description": "Has dominado el arte de organizar la información resolviendo 10 problemas de estructuras de datos.",
        "image_url": "https://img.icons8.com/color/96/000000/database.png"
    },
    {
        "stable_id": "ACH_PERFECTIONIST",
        "title": "Perfeccionista",
        "description": "Resolviste 5 problemas diferentes al primer intento (AC directo).",
        "image_url": "https://img.icons8.com/color/96/000000/prize.png"
    },
    {
        "stable_id": "ACH_STREAK_7",
        "title": "Adicción al Código",
        "description": "¡Imparable! Mantuviste una racha de 7 días consecutivos resolviendo problemas.",
        "image_url": "https://img.icons8.com/color/96/000000/campfire.png"
    },
    {
        "stable_id": "ACH_GLADIATOR",
        "title": "Gladiador",
        "description": "Valiente en la arena. Participaste y obtuviste puntos en tu primer Reto Semanal.",
        "image_url": "https://img.icons8.com/color/96/000000/spartan-helmet.png"
    },
    {
        "stable_id": "ACH_MASTERY_100",
        "title": "Dominio Total",
        "description": "Alcanzaste el 100% de maestría en una habilidad específica en tu Grafo de Conocimientos.",
        "image_url": "https://img.icons8.com/color/96/000000/crown.png"
    },
    {
        "stable_id": "ACH_DP_MASTER",
        "title": "Maestro Dinámico",
        "description": "Resolviste 5 problemas de Programación Dinámica.",
        "image_url": "https://img.icons8.com/color/96/000000/brain.png"
    },
    {
        "stable_id": "ACH_SPEED_DEMON",
        "title": "Demonio de la Velocidad",
        "description": "Resolviste un problema de dificultad media o alta en menos de 10 minutos desde que lo abriste.",
        "image_url": "https://img.icons8.com/color/96/000000/stopwatch.png"
    }
]

def run():
    print("Iniciando población de insignias (Achievements)...")
    
    created_count = 0
    updated_count = 0
    
    for ach_data in achievements_data:
        achievement, created = Achievement.objects.update_or_create(
            stable_id=ach_data["stable_id"],
            defaults={
                "title": ach_data["title"],
                "description": ach_data["description"],
                "image_url": ach_data["image_url"]
            }
        )
        if created:
            created_count += 1
        else:
            updated_count += 1
            
    print(f"¡Éxito! Se crearon {created_count} insignias nuevas y se actualizaron {updated_count}.")
    
    # Asignar insignias de demostración al usuario administrador
    from accounts.models import User
    from gamification.models import UserAchievement
    
    admin_user = User.objects.filter(email='admin@sempia.com').first()
    if admin_user:
        print("Asignando insignias de prueba al usuario administrador...")
        ach1 = Achievement.objects.get(stable_id="ACH_FIRST_BLOOD")
        ach2 = Achievement.objects.get(stable_id="ACH_FAST_MIND")
        ach3 = Achievement.objects.get(stable_id="ACH_GRAPH_KING")
        
        UserAchievement.objects.get_or_create(
            user=admin_user, achievement=ach1, defaults={"reason": "Primer problema resuelto: Two Sum."}
        )
        UserAchievement.objects.get_or_create(
            user=admin_user, achievement=ach2, defaults={"reason": "Problema resuelto al primer intento."}
        )
        UserAchievement.objects.get_or_create(
            user=admin_user, achievement=ach3, defaults={"reason": "Has conquistado 5 grafos."}
        )
        print("Insignias de demostración asignadas.")

if __name__ == '__main__':
    run()
