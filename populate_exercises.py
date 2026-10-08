import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from exercises.models import Exercise, TestCase, ExerciseSkill
from skills.models import Skill
from accounts.models import User

def get_admin_user():
    user = User.objects.filter(username='admin').first()
    if not user:
        user = User.objects.create_superuser('admin@sempia.com', 'admin', 'admin')
    return user

exercises_data = [
    # Arreglos y Strings, Complejidad, Dos Punteros
    {
        "stable_id": "EX_001",
        "title": "Suma de Dos",
        "statement": "Dado un arreglo de números enteros ordenado de forma ascendente, y un número objetivo (target). Encuentra dos números en el arreglo que sumen el objetivo y devuelve sus índices (basado en 0). Asume que siempre hay exactamente una solución. Intenta hacerlo en O(N) de complejidad de tiempo usando dos punteros.",
        "difficulty": 100,
        "skills": ["arreglos_strings", "dos_punteros", "complejidad"],
        "test_cases": [
            {"inputs": "4\n2 7 11 15\n9", "expected_outputs": "0 1", "case_type": "VISIBLE"},
            {"inputs": "3\n3 2 4\n6", "expected_outputs": "1 2", "case_type": "HIDDEN"},
            {"inputs": "2\n3 3\n6", "expected_outputs": "0 1", "case_type": "HIDDEN"}
        ]
    },
    {
        "stable_id": "EX_002",
        "title": "Palíndromo Válido",
        "statement": "Dada una cadena de texto, determina si es un palíndromo (se lee igual de izquierda a derecha que de derecha a izquierda), considerando únicamente caracteres alfanuméricos y omitiendo espacios o signos de puntuación. Ignora mayúsculas y minúsculas.",
        "difficulty": 100,
        "skills": ["arreglos_strings", "dos_punteros"],
        "test_cases": [
            {"inputs": "A man, a plan, a canal: Panama", "expected_outputs": "true", "case_type": "VISIBLE"},
            {"inputs": "race a car", "expected_outputs": "false", "case_type": "HIDDEN"},
            {"inputs": " ", "expected_outputs": "true", "case_type": "HIDDEN"}
        ]
    },
    # Hash Tables / Maps
    {
        "stable_id": "EX_003",
        "title": "Anagramas",
        "statement": "Dadas dos cadenas de texto S y T, devuelve verdadero si T es un anagrama de S. Un anagrama es una palabra o frase formada al reordenar las letras de otra palabra, usando todas las letras originales exactamente una vez. Intenta usar mapas/frecuencias para resolverlo de forma óptima.",
        "difficulty": 100,
        "skills": ["arreglos_strings", "tablas_hash"],
        "test_cases": [
            {"inputs": "anagram\nnagaram", "expected_outputs": "true", "case_type": "VISIBLE"},
            {"inputs": "rat\ncar", "expected_outputs": "false", "case_type": "HIDDEN"}
        ]
    },
    {
        "stable_id": "EX_004",
        "title": "Frecuencia de Elementos",
        "statement": "Se te da un arreglo de N números. Encuentra el elemento que más se repite. Si hay un empate, imprime el número menor. Se recomienda el uso de tablas hash para llevar la cuenta eficientemente.",
        "difficulty": 100,
        "skills": ["tablas_hash", "complejidad"],
        "test_cases": [
            {"inputs": "5\n1 3 1 3 2", "expected_outputs": "1", "case_type": "VISIBLE"},
            {"inputs": "3\n5 5 5", "expected_outputs": "5", "case_type": "HIDDEN"}
        ]
    },
    # Ventana Deslizante (Sliding Window)
    {
        "stable_id": "EX_005",
        "title": "Suma Máxima en Subarreglo de Tamaño K",
        "statement": "Dado un arreglo de N enteros positivos y un entero K, calcula la suma máxima de cualquier subarreglo contiguo de tamaño exactamente K.",
        "difficulty": 200,
        "skills": ["arreglos_strings", "sliding_window"],
        "test_cases": [
            {"inputs": "6 3\n2 1 5 1 3 2", "expected_outputs": "9", "case_type": "VISIBLE"},
            {"inputs": "5 2\n2 3 4 1 5", "expected_outputs": "7", "case_type": "HIDDEN"}
        ]
    },
    {
        "stable_id": "EX_006",
        "title": "Subcadena más Larga Sin Repetir",
        "statement": "Dada una cadena de texto, encuentra la longitud de la subcadena continua más larga sin caracteres repetidos. Usa una ventana deslizante para optimizar tu solución.",
        "difficulty": 200,
        "skills": ["arreglos_strings", "sliding_window", "tablas_hash"],
        "test_cases": [
            {"inputs": "abcabcbb", "expected_outputs": "3", "case_type": "VISIBLE"},
            {"inputs": "bbbbb", "expected_outputs": "1", "case_type": "HIDDEN"},
            {"inputs": "pwwkew", "expected_outputs": "3", "case_type": "HIDDEN"}
        ]
    },
    # Sumas Prefijas
    {
        "stable_id": "EX_007",
        "title": "Consultas de Suma de Rangos",
        "statement": "Tienes un arreglo de N números. Luego recibes Q consultas. Cada consulta consta de dos índices L y R. Debes imprimir la suma de los elementos en el arreglo desde el índice L hasta el índice R (inclusivos, basados en 0). Calcula las respuestas rápidamente usando sumas prefijas.",
        "difficulty": 200,
        "skills": ["arreglos_strings", "prefix_sum"],
        "test_cases": [
            {"inputs": "5\n-2 0 3 -5 2\n2\n0 2\n2 4", "expected_outputs": "1\n0", "case_type": "VISIBLE"},
            {"inputs": "3\n1 2 3\n1\n0 2", "expected_outputs": "6", "case_type": "HIDDEN"}
        ]
    },
    {
        "stable_id": "EX_008",
        "title": "Subarreglo con Suma Cero",
        "statement": "Dado un arreglo de enteros, determina si existe un subarreglo continuo cuya suma sea exactamente 0. Imprime 'true' si existe, o 'false' en caso contrario. Piensa en cómo las sumas prefijas y los mapas pueden ayudarte a lograr O(N).",
        "difficulty": 200,
        "skills": ["prefix_sum", "tablas_hash"],
        "test_cases": [
            {"inputs": "5\n4 2 -3 1 6", "expected_outputs": "true", "case_type": "VISIBLE"},
            {"inputs": "4\n1 2 3 4", "expected_outputs": "false", "case_type": "HIDDEN"}
        ]
    },
    # Manipulación de Bits
    {
        "stable_id": "EX_009",
        "title": "Número Único",
        "statement": "Dado un arreglo no vacío de números enteros, cada elemento aparece dos veces excepto uno. Encuentra ese elemento único. Debes implementar una solución con complejidad de tiempo O(N) y usar solo espacio extra constante O(1). Las operaciones a nivel de bits son perfectas aquí.",
        "difficulty": 200,
        "skills": ["bit_manipulation", "arreglos_strings"],
        "test_cases": [
            {"inputs": "3\n2 2 1", "expected_outputs": "1", "case_type": "VISIBLE"},
            {"inputs": "5\n4 1 2 1 2", "expected_outputs": "4", "case_type": "HIDDEN"}
        ]
    },
    {
        "stable_id": "EX_010",
        "title": "Conteo de Bits (Hamming Weight)",
        "statement": "Dado un entero sin signo representado en formato decimal, calcula el número de bits que están encendidos ('1') en su representación binaria.",
        "difficulty": 100,
        "skills": ["bit_manipulation"],
        "test_cases": [
            {"inputs": "11", "expected_outputs": "3", "case_type": "VISIBLE"},
            {"inputs": "128", "expected_outputs": "1", "case_type": "HIDDEN"}
        ]
    },
    # Búsqueda Binaria
    {
        "stable_id": "EX_011",
        "title": "Búsqueda Rápida",
        "statement": "Dado un arreglo de enteros ordenados en orden ascendente y un entero 'objetivo', escribe una función para buscar el 'objetivo' en el arreglo usando búsqueda binaria. Si existe, devuelve su índice (0-indexado). De lo contrario, devuelve -1.",
        "difficulty": 100,
        "skills": ["busqueda_binaria", "arreglos_strings", "complejidad"],
        "test_cases": [
            {"inputs": "6\n-1 0 3 5 9 12\n9", "expected_outputs": "4", "case_type": "VISIBLE"},
            {"inputs": "6\n-1 0 3 5 9 12\n2", "expected_outputs": "-1", "case_type": "HIDDEN"}
        ]
    },
    {
        "stable_id": "EX_012",
        "title": "Posición de Inserción",
        "statement": "Dado un arreglo ordenado de enteros distintos y un valor objetivo, devuelve el índice si el objetivo es encontrado. Si no, devuelve el índice donde debería ser insertado para que el arreglo siga ordenado. Tu algoritmo debe tener complejidad O(log N).",
        "difficulty": 200,
        "skills": ["busqueda_binaria"],
        "test_cases": [
            {"inputs": "4\n1 3 5 6\n5", "expected_outputs": "2", "case_type": "VISIBLE"},
            {"inputs": "4\n1 3 5 6\n2", "expected_outputs": "1", "case_type": "HIDDEN"},
            {"inputs": "4\n1 3 5 6\n7", "expected_outputs": "4", "case_type": "HIDDEN"}
        ]
    },
    # Pilas y Colas
    {
        "stable_id": "EX_013",
        "title": "Paréntesis Válidos",
        "statement": "Dada una cadena de texto s que contiene únicamente los caracteres '(', ')', '{', '}', '[' y ']', determina si la cadena de entrada es válida. Una cadena es válida si los corchetes abiertos son cerrados por el mismo tipo de corchetes y en el orden correcto.",
        "difficulty": 200,
        "skills": ["pilas_colas", "arreglos_strings"],
        "test_cases": [
            {"inputs": "()[]{}", "expected_outputs": "true", "case_type": "VISIBLE"},
            {"inputs": "([)]", "expected_outputs": "false", "case_type": "HIDDEN"},
            {"inputs": "{[]}", "expected_outputs": "true", "case_type": "HIDDEN"}
        ]
    },
    {
        "stable_id": "EX_014",
        "title": "Temperaturas Diarias",
        "statement": "Dado un arreglo de enteros `temperaturas` que representa las temperaturas diarias, devuelve un arreglo donde el i-ésimo elemento es el número de días que debes esperar después del i-ésimo día para tener una temperatura más cálida. Si no hay ningún día futuro más cálido, pon 0 en esa posición. Se recomienda usar una pila monótona.",
        "difficulty": 200,
        "skills": ["pilas_colas", "arreglos_strings"],
        "test_cases": [
            {"inputs": "8\n73 74 75 71 69 72 76 73", "expected_outputs": "1 1 4 2 1 1 0 0", "case_type": "VISIBLE"},
            {"inputs": "4\n30 40 50 60", "expected_outputs": "1 1 1 0", "case_type": "HIDDEN"}
        ]
    },
    # Colas de Prioridad
    {
        "stable_id": "EX_015",
        "title": "K-ésimo Elemento Más Grande",
        "statement": "Dado un arreglo de enteros no ordenado y un número entero K, encuentra el K-ésimo elemento más grande del arreglo. Intenta hacerlo eficientemente insertando los elementos en una cola de prioridad (min-heap) de tamaño K.",
        "difficulty": 200,
        "skills": ["colas_prioridad", "arreglos_strings"],
        "test_cases": [
            {"inputs": "6 2\n3 2 1 5 6 4", "expected_outputs": "5", "case_type": "VISIBLE"},
            {"inputs": "9 4\n3 2 3 1 2 4 5 5 6", "expected_outputs": "4", "case_type": "HIDDEN"}
        ]
    },
    {
        "stable_id": "EX_016",
        "title": "Fusión de Listas Ordenadas",
        "statement": "Se te dan K arreglos, cada uno ya ordenado en orden ascendente. Fusiona todos los arreglos en un solo arreglo ordenado y devuélvelo. Una cola de prioridad es ideal para tomar siempre el elemento mínimo actual de todas las cabezas de lista.",
        "difficulty": 300,
        "skills": ["colas_prioridad"],
        "test_cases": [
            {"inputs": "3\n3\n1 4 5\n3\n1 3 4\n2\n2 6", "expected_outputs": "1 1 2 3 4 4 5 6", "case_type": "VISIBLE"},
            {"inputs": "2\n2\n1 2\n2\n3 4", "expected_outputs": "1 2 3 4", "case_type": "HIDDEN"}
        ]
    },
    # Recursión Básica y Backtracking
    {
        "stable_id": "EX_017",
        "title": "Fibonacci Recursivo",
        "statement": "Implementa una función recursiva para calcular el N-ésimo número de Fibonacci. F(0) = 0, F(1) = 1, y F(n) = F(n-1) + F(n-2) para n > 1.",
        "difficulty": 100,
        "skills": ["recursion", "matematicas_basicas"],
        "test_cases": [
            {"inputs": "2", "expected_outputs": "1", "case_type": "VISIBLE"},
            {"inputs": "4", "expected_outputs": "3", "case_type": "HIDDEN"},
            {"inputs": "6", "expected_outputs": "8", "case_type": "HIDDEN"}
        ]
    },
    {
        "stable_id": "EX_018",
        "title": "Subconjuntos (Subsets)",
        "statement": "Dado un arreglo de enteros únicos, devuelve todos sus posibles subconjuntos (el conjunto potencia). La solución no debe contener subconjuntos duplicados. Imprime cada subconjunto en una línea, con los elementos separados por espacios, y primero imprime los conjuntos de menor longitud. Usa backtracking.",
        "difficulty": 300,
        "skills": ["recursion", "backtracking"],
        "test_cases": [
            {"inputs": "2\n1 2", "expected_outputs": "\n1\n2\n1 2", "case_type": "VISIBLE"},
            {"inputs": "1\n0", "expected_outputs": "\n0", "case_type": "HIDDEN"}
        ]
    },
    {
        "stable_id": "EX_019",
        "title": "Permutaciones",
        "statement": "Dado un arreglo de N enteros distintos, devuelve todas las permutaciones posibles de esos números. Imprímelas en cualquier orden, una por línea. Utiliza el paradigma de Backtracking.",
        "difficulty": 300,
        "skills": ["backtracking"],
        "test_cases": [
            {"inputs": "3\n1 2 3", "expected_outputs": "1 2 3\n1 3 2\n2 1 3\n2 3 1\n3 1 2\n3 2 1", "case_type": "VISIBLE"},
            {"inputs": "2\n0 1", "expected_outputs": "0 1\n1 0", "case_type": "HIDDEN"}
        ]
    },
    # Algoritmos Ávidos (Greedy)
    {
        "stable_id": "EX_020",
        "title": "Asignación de Galletas",
        "statement": "Asume que eres un padre y quieres dar galletas a tus hijos. Cada hijo `i` tiene un factor de avaricia `g[i]`, que es el tamaño mínimo de galleta con el que estará contento; y cada galleta `j` tiene un tamaño `s[j]`. Si `s[j] >= g[i]`, puedes asignarle la galleta `j` al hijo `i` y el hijo estará contento. Encuentra el número máximo de hijos contentos.",
        "difficulty": 200,
        "skills": ["greedy", "arreglos_strings"],
        "test_cases": [
            {"inputs": "3\n1 2 3\n2\n1 1", "expected_outputs": "1", "case_type": "VISIBLE"},
            {"inputs": "2\n1 2\n3\n1 2 3", "expected_outputs": "2", "case_type": "HIDDEN"}
        ]
    },
    {
        "stable_id": "EX_021",
        "title": "Reuniones Máximas",
        "statement": "Te dan los horarios de inicio y fin de N reuniones. Una misma persona solo puede asistir a una reunión a la vez. Encuentra el número máximo de reuniones a las que puede asistir. Usa un enfoque Greedy ordenando por tiempo de finalización.",
        "difficulty": 200,
        "skills": ["greedy", "arreglos_strings"],
        "test_cases": [
            {"inputs": "3\n1 3\n2 4\n3 5", "expected_outputs": "2", "case_type": "VISIBLE"},
            {"inputs": "4\n1 2\n2 3\n3 4\n4 5", "expected_outputs": "4", "case_type": "HIDDEN"}
        ]
    },
    # Matemáticas Básicas y Geometría, Teoría de Números, Aritmética Modular
    {
        "stable_id": "EX_022",
        "title": "Máximo Común Divisor (GCD)",
        "statement": "Dados dos números enteros A y B, calcula su Máximo Común Divisor (GCD) utilizando el algoritmo de Euclides.",
        "difficulty": 100,
        "skills": ["matematicas_basicas", "teoria_numeros"],
        "test_cases": [
            {"inputs": "48 18", "expected_outputs": "6", "case_type": "VISIBLE"},
            {"inputs": "101 103", "expected_outputs": "1", "case_type": "HIDDEN"}
        ]
    },
    {
        "stable_id": "EX_023",
        "title": "Números Primos (Criba)",
        "statement": "Dado un número entero N, imprime el número de números primos que son estrictamente menores que N. Se recomienda usar la Criba de Eratóstenes para lograrlo eficientemente.",
        "difficulty": 200,
        "skills": ["teoria_numeros", "matematicas_basicas"],
        "test_cases": [
            {"inputs": "10", "expected_outputs": "4", "case_type": "VISIBLE"},
            {"inputs": "0", "expected_outputs": "0", "case_type": "HIDDEN"},
            {"inputs": "100", "expected_outputs": "25", "case_type": "HIDDEN"}
        ]
    },
    {
        "stable_id": "EX_024",
        "title": "Exponenciación Rápida",
        "statement": "Calcula `(x^n) % m`, donde x es la base, n es el exponente y m es el módulo. Debes hacerlo en tiempo O(log n) usando exponenciación binaria (rápida).",
        "difficulty": 300,
        "skills": ["aritmetica_modular", "recursion"],
        "test_cases": [
            {"inputs": "2 10 1000", "expected_outputs": "24", "case_type": "VISIBLE"},
            {"inputs": "5 3 100", "expected_outputs": "25", "case_type": "HIDDEN"}
        ]
    },
    {
        "stable_id": "EX_025",
        "title": "Inverso Modular",
        "statement": "Dado un entero a y un módulo primo m, encuentra el inverso multiplicativo modular de a bajo módulo m (es decir, un x tal que (a * x) % m == 1). Puedes usar el Pequeño Teorema de Fermat porque m es primo.",
        "difficulty": 300,
        "skills": ["aritmetica_modular", "teoria_numeros"],
        "test_cases": [
            {"inputs": "3 11", "expected_outputs": "4", "case_type": "VISIBLE"},
            {"inputs": "10 17", "expected_outputs": "12", "case_type": "HIDDEN"}
        ]
    },
    # Representación de Grafos, BFS, DFS
    {
        "stable_id": "EX_026",
        "title": "Contar Componentes Conectadas",
        "statement": "Dado un grafo no dirigido con V vértices (numerados de 0 a V-1) y E aristas, encuentra el número total de componentes conectadas. Usa una matriz o lista de adyacencia y DFS/BFS para recorrerlo.",
        "difficulty": 200,
        "skills": ["grafos_representacion", "dfs"],
        "test_cases": [
            {"inputs": "5 3\n0 1\n1 2\n3 4", "expected_outputs": "2", "case_type": "VISIBLE"},
            {"inputs": "4 0", "expected_outputs": "4", "case_type": "HIDDEN"}
        ]
    },
    {
        "stable_id": "EX_027",
        "title": "Distancia a la Raíz",
        "statement": "Dado un árbol sin raíz en forma de grafo no dirigido, y considerando el vértice 0 como la raíz, calcula la distancia (número de aristas) desde la raíz a todos los demás vértices. Imprímelas separadas por espacios. Un BFS es la mejor opción.",
        "difficulty": 200,
        "skills": ["grafos_representacion", "bfs"],
        "test_cases": [
            {"inputs": "4\n0 1\n0 2\n1 3", "expected_outputs": "0 1 1 2", "case_type": "VISIBLE"},
            {"inputs": "5\n0 1\n1 2\n2 3\n3 4", "expected_outputs": "0 1 2 3 4", "case_type": "HIDDEN"}
        ]
    },
    # DSU y Topological Sort
    {
        "stable_id": "EX_028",
        "title": "Conexiones Redundantes (Ciclos)",
        "statement": "En un grafo inicialmente vacío con N nodos, se van agregando aristas una por una. Detecta en qué momento se forma el primer ciclo y reporta si hay ciclo o no. La estructura de Conjuntos Disjuntos (Union-Find) te permite saber en O(1) amortizado si dos nodos ya estaban conectados.",
        "difficulty": 300,
        "skills": ["dsu", "grafos_representacion"],
        "test_cases": [
            {"inputs": "3 3\n0 1\n1 2\n0 2", "expected_outputs": "true", "case_type": "VISIBLE"},
            {"inputs": "4 3\n0 1\n1 2\n2 3", "expected_outputs": "false", "case_type": "HIDDEN"}
        ]
    },
    {
        "stable_id": "EX_029",
        "title": "Horario de Clases",
        "statement": "Hay N cursos que debes tomar, etiquetados de 0 a N-1. Se te da una lista de prerrequisitos donde prerrequisitos[i] = [a, b] indica que debes tomar b primero si quieres tomar a. Retorna si es posible terminar todos los cursos. Piensa en detectar ciclos en grafos dirigidos o usar Ordenamiento Topológico (Kahn's Algorithm).",
        "difficulty": 300,
        "skills": ["topological_sort", "grafos_representacion", "bfs"],
        "test_cases": [
            {"inputs": "2 1\n1 0", "expected_outputs": "true", "case_type": "VISIBLE"},
            {"inputs": "2 2\n1 0\n0 1", "expected_outputs": "false", "case_type": "HIDDEN"}
        ]
    },
    {
        "stable_id": "EX_030",
        "title": "Orden de Tareas",
        "statement": "Similar a Horario de Clases, tienes N tareas y prerrequisitos direccionales (u -> v, v depende de u). Devuelve un orden válido de tareas para realizarlas todas usando Ordenamiento Topológico. Si hay varias respuestas, cualquiera es válida. Si es imposible, imprime 'Imposible'.",
        "difficulty": 300,
        "skills": ["topological_sort", "dfs"],
        "test_cases": [
            {"inputs": "4 4\n0 1\n0 2\n1 3\n2 3", "expected_outputs": "0 1 2 3", "case_type": "VISIBLE"},
            {"inputs": "2 2\n0 1\n1 0", "expected_outputs": "Imposible", "case_type": "HIDDEN"}
        ]
    },
    # Árboles
    {
        "stable_id": "EX_031",
        "title": "Profundidad Máxima de Árbol",
        "statement": "Dado un árbol general (donde cada nodo puede tener varios hijos), representado por pares (padre, hijo) siendo 0 la raíz, calcula la profundidad máxima o altura del árbol. El árbol tiene N nodos.",
        "difficulty": 200,
        "skills": ["arboles_basico", "dfs"],
        "test_cases": [
            {"inputs": "5\n0 1\n0 2\n1 3\n1 4", "expected_outputs": "2", "case_type": "VISIBLE"},
            {"inputs": "2\n0 1", "expected_outputs": "1", "case_type": "HIDDEN"}
        ]
    },
    {
        "stable_id": "EX_032",
        "title": "Invertir Árbol Binario",
        "statement": "Dado un árbol binario representado en formato de arreglo donde cada i tiene a (2*i + 1) como hijo izquierdo y (2*i + 2) como hijo derecho. Imprime el arreglo resultante después de intercambiar el subárbol izquierdo y derecho de todos los nodos. Las posiciones vacías son representadas por -1.",
        "difficulty": 200,
        "skills": ["arboles_basico", "recursion"],
        "test_cases": [
            {"inputs": "7\n4 2 7 1 3 6 9", "expected_outputs": "4 7 2 9 6 3 1", "case_type": "VISIBLE"},
            {"inputs": "3\n2 1 3", "expected_outputs": "2 3 1", "case_type": "HIDDEN"}
        ]
    },
    # Complementary for missing ones to reach 2 per skill
    {
        "stable_id": "EX_033",
        "title": "Encontrar el Defecto (Union-Find)",
        "statement": "Tienes N máquinas en una red. Te dan una serie de operaciones: 1 u v (conecta u y v), y 2 u v (pregunta si u y v están en la misma red). Para cada consulta 2, imprime '1' si lo están, o '0' si no. Implementa la estructura de Conjuntos Disjuntos.",
        "difficulty": 300,
        "skills": ["dsu"],
        "test_cases": [
            {"inputs": "4 4\n1 0 1\n2 0 1\n1 2 3\n2 1 2", "expected_outputs": "1\n0", "case_type": "VISIBLE"},
            {"inputs": "2 2\n2 0 1\n1 0 1", "expected_outputs": "0", "case_type": "HIDDEN"}
        ]
    }
]

def run():
    print("Iniciando población de ejercicios...")
    
    admin = get_admin_user()
    
    exercises_created = 0
    test_cases_created = 0
    
    for ex_data in exercises_data:
        # Check if already exists
        if Exercise.objects.filter(stable_id=ex_data["stable_id"]).exists():
            print(f"El ejercicio {ex_data['stable_id']} ya existe. Actualizándolo...")
            exercise = Exercise.objects.get(stable_id=ex_data["stable_id"])
            exercise.title = ex_data["title"]
            exercise.statement = ex_data["statement"]
            exercise.difficulty = ex_data["difficulty"]
            exercise.status = Exercise.Status.PUBLISHED
            exercise.author = admin
            exercise.save()
        else:
            exercise = Exercise.objects.create(
                stable_id=ex_data["stable_id"],
                title=ex_data["title"],
                statement=ex_data["statement"],
                difficulty=ex_data["difficulty"],
                status=Exercise.Status.PUBLISHED,
                author=admin
            )
            exercises_created += 1
            
        # Add skills
        exercise.skills.clear()
        for skill_id in ex_data["skills"]:
            try:
                skill_obj = Skill.objects.get(name=get_skill_name_from_id(skill_id))
                ExerciseSkill.objects.get_or_create(exercise=exercise, skill=skill_obj)
            except Skill.DoesNotExist:
                print(f"ADVERTENCIA: La habilidad {skill_id} no se encontró en la BD.")
                
        # Add test cases
        exercise.test_cases.all().delete()
        for tc_data in ex_data["test_cases"]:
            TestCase.objects.create(
                exercise=exercise,
                inputs=tc_data["inputs"],
                expected_outputs=tc_data["expected_outputs"],
                case_type=tc_data["case_type"]
            )
            test_cases_created += 1
            
    print(f"¡Éxito! Se crearon {exercises_created} ejercicios y {test_cases_created} casos de prueba nuevos.")
    
def get_skill_name_from_id(skill_id):
    # Map the internal string ID from json to the DB skill name
    skill_map = {
        "complejidad": "Análisis de Complejidad (Big O)",
        "arreglos_strings": "Arreglos y Strings",
        "tablas_hash": "Hash Tables / Maps",
        "dos_punteros": "Dos Punteros (Two Pointers)",
        "sliding_window": "Ventana Deslizante (Sliding Window)",
        "prefix_sum": "Sumas Prefijas (Prefix Sums)",
        "bit_manipulation": "Manipulación de Bits",
        "busqueda_binaria": "Búsqueda Binaria",
        "pilas_colas": "Pilas y Colas (Stacks & Queues)",
        "colas_prioridad": "Colas de Prioridad (Heaps)",
        "recursion": "Recursión Básica",
        "backtracking": "Backtracking",
        "greedy": "Algoritmos Ávidos (Greedy)",
        "matematicas_basicas": "Matemáticas Básicas y Geometría simple",
        "teoria_numeros": "Teoría de Números (Criba, GCD, LCM)",
        "aritmetica_modular": "Aritmética Modular y Exponenciación Rápida",
        "grafos_representacion": "Representación de Grafos",
        "bfs": "Búsqueda en Anchura (BFS)",
        "dfs": "Búsqueda en Profundidad (DFS)",
        "dsu": "Disjoint Set Union (Union-Find)",
        "topological_sort": "Ordenamiento Topológico",
        "arboles_basico": "Árboles Binarios y BST"
    }
    return skill_map.get(skill_id, skill_id)

if __name__ == '__main__':
    run()
