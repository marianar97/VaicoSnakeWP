from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from charts.models import Result


# Create your views here.
def charts(request):
    logged_in_user_posts = Result.objects.filter(user=request.user.id)
    print('user, ', request.user.id)
    print('*' * 10)
    for post in logged_in_user_posts:
        print('images')
        print(post.images)
    print('logged in users ', logged_in_user_posts)
    print('*' * 10)
    return render(request, 'charts/chart.html',  {'posts' : logged_in_user_posts}  )



