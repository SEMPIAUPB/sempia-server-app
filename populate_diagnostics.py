import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from skills.models import Skill, DiagnosticQuestion, DiagnosticChoice

# Define the theoretical questions
questions_data = [
    # Complejidad
    {
        "skill_name": "Análisis de Complejidad (Big O)",
        "text": "¿Cuál es la complejidad temporal en el peor de los casos para buscar un elemento en un arreglo no ordenado de N elementos?",
        "difficulty": "EASY",
        "choices": [
            {"text": "O(1)", "is_correct": False},
            {"text": "O(log N)", "is_correct": False},
            {"text": "O(N)", "is_correct": True},
            {"text": "O(N log N)", "is_correct": False}
        ]
    },
    {
        "skill_name": "Análisis de Complejidad (Big O)",
        "text": "¿Qué representa la notación Big O en el análisis de algoritmos?",
        "difficulty": "MEDIUM",
        "choices": [
            {"text": "El tiempo mínimo exacto que tarda un algoritmo en ejecutarse en milisegundos.", "is_correct": False},
            {"text": "El límite superior asintótico del crecimiento del tiempo de ejecución o espacio de memoria.", "is_correct": True},
            {"text": "La cantidad exacta de memoria RAM que consumirá el programa.", "is_correct": False},
            {"text": "El tiempo promedio de ejecución considerando todas las entradas posibles.", "is_correct": False}
        ]
    },
    {
        "skill_name": "Análisis de Complejidad (Big O)",
        "text": "Si un algoritmo procesa cada elemento de un arreglo iterándolo por completo, y dentro de ese bucle llama a una función que toma tiempo O(log N), ¿cuál es la complejidad total?",
        "difficulty": "MEDIUM",
        "choices": [
            {"text": "O(N)", "is_correct": False},
            {"text": "O(N log N)", "is_correct": True},
            {"text": "O(N^2)", "is_correct": False},
            {"text": "O(log N)", "is_correct": False}
        ]
    },
    # Arreglos y Strings
    {
        "skill_name": "Arreglos y Strings",
        "text": "En un arreglo estático continuo en memoria, ¿cuál es el costo de acceder al i-ésimo elemento?",
        "difficulty": "EASY",
        "choices": [
            {"text": "O(1)", "is_correct": True},
            {"text": "O(i)", "is_correct": False},
            {"text": "O(N)", "is_correct": False},
            {"text": "O(log N)", "is_correct": False}
        ]
    },
    {
        "skill_name": "Arreglos y Strings",
        "text": "¿Por qué concatenar strings usando `s = s + caracter` dentro de un bucle puede ser ineficiente en lenguajes como Java o Python?",
        "difficulty": "MEDIUM",
        "choices": [
            {"text": "Porque los caracteres no se pueden sumar matemáticamente.", "is_correct": False},
            {"text": "Porque los strings son inmutables y concatenar requiere crear un nuevo string copiando todos los caracteres previos (tomando O(N^2) en total).", "is_correct": True},
            {"text": "Porque el compilador no puede predecir el tamaño del string y lanza una excepción de memoria.", "is_correct": False},
            {"text": "No es ineficiente, es la forma óptima de construir un string.", "is_correct": False}
        ]
    },
    # Pilas y Colas
    {
        "skill_name": "Pilas y Colas (Stacks & Queues)",
        "text": "¿Cuál es el principio fundamental de operación de una estructura de datos tipo Pila (Stack)?",
        "difficulty": "EASY",
        "choices": [
            {"text": "FIFO (First In, First Out)", "is_correct": False},
            {"text": "LIFO (Last In, First Out)", "is_correct": True},
            {"text": "Aleatorio", "is_correct": False},
            {"text": "El elemento de mayor valor sale primero", "is_correct": False}
        ]
    },
    {
        "skill_name": "Pilas y Colas (Stacks & Queues)",
        "text": "Si se encolan los elementos A, B y C en una Cola (Queue) en ese orden, y luego se hacen dos operaciones 'Dequeue' (desencolar), ¿qué elemento(s) se obtienen?",
        "difficulty": "EASY",
        "choices": [
            {"text": "B y luego C", "is_correct": False},
            {"text": "A y luego B", "is_correct": True},
            {"text": "C y luego B", "is_correct": False},
            {"text": "Solo se obtiene C", "is_correct": False}
        ]
    },
    # Tablas Hash
    {
        "skill_name": "Hash Tables / Maps",
        "text": "En promedio, ¿cuál es la complejidad temporal de búsqueda, inserción y eliminación en una Tabla Hash con una buena función hash?",
        "difficulty": "EASY",
        "choices": [
            {"text": "O(log N)", "is_correct": False},
            {"text": "O(1)", "is_correct": True},
            {"text": "O(N)", "is_correct": False},
            {"text": "O(N log N)", "is_correct": False}
        ]
    },
    {
        "skill_name": "Hash Tables / Maps",
        "text": "¿Qué ocurre cuando dos llaves distintas generan el mismo valor hash en una Tabla Hash?",
        "difficulty": "MEDIUM",
        "choices": [
            {"text": "El programa lanza una excepción y se detiene.", "is_correct": False},
            {"text": "El valor anterior es sobrescrito inmediatamente por el nuevo.", "is_correct": False},
            {"text": "Se produce una 'colisión', la cual debe resolverse usando técnicas como encadenamiento o direccionamiento abierto.", "is_correct": True},
            {"text": "La tabla hash se vacía automáticamente para hacer espacio.", "is_correct": False}
        ]
    },
    # Recursión Básica
    {
        "skill_name": "Recursión Básica",
        "text": "¿Qué elemento es estrictamente obligatorio para que una función recursiva no se ejecute infinitamente (hasta causar StackOverflow)?",
        "difficulty": "EASY",
        "choices": [
            {"text": "Un bucle 'while' dentro de la función.", "is_correct": False},
            {"text": "Una variable global.", "is_correct": False},
            {"text": "Un caso base o condición de parada.", "is_correct": True},
            {"text": "Un límite de tiempo (timeout) explícito.", "is_correct": False}
        ]
    },
    {
        "skill_name": "Recursión Básica",
        "text": "Si cada llamada recursiva de una función genera exactamente 2 nuevas llamadas, ¿qué forma tendrá el árbol de llamadas y cuál será su número total de nodos para una profundidad D?",
        "difficulty": "HARD",
        "choices": [
            {"text": "Forma lineal, con D nodos en total.", "is_correct": False},
            {"text": "Forma de árbol binario perfecto, con aproximadamente 2^D nodos en total.", "is_correct": True},
            {"text": "Forma de grafo acíclico, con D^2 nodos en total.", "is_correct": False},
            {"text": "Forma de árbol de segmentos, con log(D) nodos en total.", "is_correct": False}
        ]
    },
    # Búsqueda Binaria
    {
        "skill_name": "Búsqueda Binaria",
        "text": "¿Cuál es la precondición obligatoria sobre los datos para poder aplicar Búsqueda Binaria de forma directa?",
        "difficulty": "EASY",
        "choices": [
            {"text": "Los datos deben estar ordenados.", "is_correct": True},
            {"text": "Los datos deben ser exclusivamente números enteros.", "is_correct": False},
            {"text": "Los datos no deben contener elementos duplicados.", "is_correct": False},
            {"text": "El tamaño del arreglo debe ser par.", "is_correct": False}
        ]
    },
    {
        "skill_name": "Búsqueda Binaria",
        "text": "¿Por qué calcular el elemento medio como `mid = (low + high) / 2` puede ser peligroso en lenguajes como C++ o Java con arreglos inmensos?",
        "difficulty": "MEDIUM",
        "choices": [
            {"text": "Porque el resultado puede ser un número con decimales y fallar al acceder al índice.", "is_correct": False},
            {"text": "Porque la suma `low + high` puede causar un desbordamiento de enteros (Integer Overflow).", "is_correct": True},
            {"text": "Porque dividir por dos es una operación matemáticamente costosa y retrasa el algoritmo.", "is_correct": False},
            {"text": "No es peligroso, es la implementación ideal en cualquier escenario.", "is_correct": False}
        ]
    },
    # Representación de Grafos
    {
        "skill_name": "Representación de Grafos",
        "text": "Para un grafo poco denso (con pocos vértices conectados entre sí comparado con el total), ¿cuál representación en memoria es más eficiente en espacio?",
        "difficulty": "MEDIUM",
        "choices": [
            {"text": "Matriz de Adyacencia", "is_correct": False},
            {"text": "Lista de Adyacencia", "is_correct": True},
            {"text": "Matriz de Incidencia", "is_correct": False},
            {"text": "Arreglo continuo simple", "is_correct": False}
        ]
    },
    {
        "skill_name": "Representación de Grafos",
        "text": "En una Matriz de Adyacencia de tamaño V x V (donde V son los vértices), ¿cuál es el costo en tiempo para saber si existe una arista directa entre el vértice i y el vértice j?",
        "difficulty": "EASY",
        "choices": [
            {"text": "O(V)", "is_correct": False},
            {"text": "O(1)", "is_correct": True},
            {"text": "O(E), siendo E el número de aristas", "is_correct": False},
            {"text": "O(log V)", "is_correct": False}
        ]
    }
]

def run():
    print("Borrando preguntas de diagnóstico previas...")
    DiagnosticQuestion.objects.all().delete()
    
    questions_created = 0
    
    for item in questions_data:
        skill_name = item['skill_name']
        try:
            skill = Skill.objects.get(name=skill_name)
        except Skill.DoesNotExist:
            print(f"La habilidad '{skill_name}' no existe en la base de datos. Saltando...")
            continue
            
        question = DiagnosticQuestion.objects.create(
            text=item['text'],
            skill=skill,
            difficulty=item['difficulty']
        )
        questions_created += 1
        
        for choice_data in item['choices']:
            DiagnosticChoice.objects.create(
                question=question,
                text=choice_data['text'],
                is_correct=choice_data['is_correct']
            )
            
    print(f"Exito! Se crearon {questions_created} preguntas para el examen diagnóstico.")

if __name__ == '__main__':
    run()
