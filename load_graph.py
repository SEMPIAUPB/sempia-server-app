import os
import django
import sys
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from skills.models import Skill

def run():
    print("Leyendo initial_graph.json...")
    with open('initial_graph.json', 'r', encoding='utf-8') as f:
        graph = json.load(f)
        
    print("Creando habilidades...")
    # First pass: Create all skills
    for item in graph:
        skill, created = Skill.objects.get_or_create(
            name=item['habilidad'],
            defaults={'category': 'General'}
        )
        if created:
            print(f"Creada habilidad: {skill.name}")
            
    # Second pass: Link prerequisites
    for item in graph:
        skill = Skill.objects.get(name=item['habilidad'])
        prereqs = item['prerrequisitos']
        for prereq_id in prereqs:
            # We need to find the name corresponding to this prereq_id in the json
            prereq_name = next((g['habilidad'] for g in graph if g['id'] == prereq_id), None)
            if prereq_name:
                prereq_skill = Skill.objects.get(name=prereq_name)
                skill.prerequisites.add(prereq_skill)
                
    print(f"Se actualizaron los prerrequisitos correctamente. Total de habilidades: {Skill.objects.count()}")

if __name__ == '__main__':
    run()
