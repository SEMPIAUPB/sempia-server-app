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
            resp = requests.post(f"{AI_WORKER_URL}/tutoring/hint", json=request.data, timeout=10)
            resp.raise_for_status()
            return Response(resp.json(), status=resp.status_code)
        except requests.RequestException as e:
            return Response({"error": "AI service unavailable", "details": str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

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
