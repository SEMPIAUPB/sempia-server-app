import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

import os

AI_WORKER_URL = os.environ.get("AI_WORKER_URL", "http://ai-worker:8001")

class DKTProxyView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            # We enforce that the student ID matches the authenticated user
            payload = request.data
            payload["student_id"] = str(request.user.id)
            
            resp = requests.post(f"{AI_WORKER_URL}/dkt/estimate", json=payload, timeout=5)
            resp.raise_for_status()
            return Response(resp.json(), status=resp.status_code)
        except requests.RequestException as e:
            return Response({"error": "AI service unavailable", "details": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class TutoringProxyView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            resp = requests.post(f"{AI_WORKER_URL}/tutoring/hint", json=request.data, timeout=25)
            resp.raise_for_status()
            return Response(resp.json(), status=resp.status_code)
        except requests.RequestException as e:
            # Fallback if AI worker is down or times out
            verdict = request.data.get("judge_verdict", "Desconocido")
            
            probable_error_type = "Desconocido"
            cause = "Tuvimos problemas conectando con la IA Tutora, pero aquí tienes una evaluación automática basada en el veredicto del juez."
            concept = "Conceptos generales"
            recommendation = "Revisa tu código paso a paso o usa casos de prueba más simples."
            hint = "Verifica la sintaxis, límites de arreglos o tipos de datos que estás usando."
            
            if verdict == "COMPILATION_ERROR":
                probable_error_type = "Error de Sintaxis o Compilación"
                concept = "Sintaxis del lenguaje"
                cause = "El código no compila. Suele faltar un punto y coma, una llave, o hay un tipo de dato incorrecto."
                recommendation = "Revisa los mensajes del compilador detenidamente para encontrar la línea con error."
                hint = "¡Tu código tiene un error de sintaxis! Revisa si te falta cerrar llaves '{}', paréntesis '()', o comillas."
            elif verdict == "RUNTIME_ERROR":
                probable_error_type = "Excepción en Tiempo de Ejecución"
                concept = "Manejo de Excepciones / Estructuras de Datos"
                cause = "El código falló mientras se ejecutaba. Posible división por cero, acceso fuera de los límites, etc."
                recommendation = "Verifica los índices de tus arreglos y asegúrate de no hacer operaciones inválidas."
                hint = "El programa se cerró inesperadamente. Revisa si estás accediendo a una posición inválida."
            elif verdict == "TIME_LIMIT_EXCEEDED":
                probable_error_type = "Límite de Tiempo Excedido (TLE)"
                concept = "Complejidad Algorítmica (Big O)"
                cause = "Tu algoritmo es correcto para casos pequeños pero es ineficiente y demasiado lento."
                recommendation = "Intenta buscar una estructura de datos más eficiente o elimina ciclos anidados."
                hint = "¡Tu solución está tomando demasiado tiempo! Intenta optimizarla (ej. O(N))."
            elif verdict == "WRONG_ANSWER":
                probable_error_type = "Respuesta Incorrecta (Lógica)"
                concept = "Lógica de Programación"
                cause = "El código compila y corre rápido, pero no produce el resultado esperado."
                recommendation = "Simula tu algoritmo en papel con casos límite."
                hint = "La respuesta generada no coincide con lo esperado. Revisa casos especiales o extremos."
            elif verdict == "MEMORY_LIMIT_EXCEEDED":
                probable_error_type = "Límite de Memoria Excedido"
                concept = "Gestión de Memoria"
                cause = "Estás guardando demasiados datos a la vez o hay recursión infinita."
                recommendation = "No almacenes todo si no es necesario."
                hint = "Tu código usa demasiada memoria. Revisa que tu recursión termine correctamente."

            fallback_response = {
                "probable_error_type": probable_error_type,
                "approximate_line": None,
                "cause_explanation": cause,
                "programming_concept": concept,
                "pedagogical_recommendation": recommendation,
                "confidence_level": "Medium (Fallback)",
                "hint_text": hint,
                "can_resubmit": True
            }
            return Response(fallback_response, status=status.HTTP_200_OK)

class InitDBView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        try:
            import load_graph
            load_graph.run()
            import populate_diagnostics
            populate_diagnostics.run()
            return Response({"status": "Success"})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
