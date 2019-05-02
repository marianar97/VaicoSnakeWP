from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.
def chart(request):
    return render(request, 'charts/chart.html')

def get_data(request):
    data = {
        "caminando": 22,
        "corriendo": 16,
    }
    return JsonResponse(data)

class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None):
        labels = ["caminando", "corriendo", "sentados"]
        default_data = [8,3,5]
        
        data = {
            "labels": labels,
            "default": default_data,
            }
        return Response(data)



