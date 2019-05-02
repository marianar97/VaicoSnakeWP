"""vaicoSnakes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from vaicoSnakes import views as local_views
from users import views as users_views
from django.conf import settings
from django.conf.urls.static import static
from charts import views as charts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', local_views.home, name='home'),
    path('contact/', local_views.contact, name='contact'),
    path('services/', local_views.services,name='services'),
    path('login/',users_views.login_view, name='login'),
    path('feed/', users_views.feed, name='feed'),
    path('logout_view/', users_views.logout_view, name='logout_view'),
    path('charts/', charts_views.chart, name='chart'),
    path('get_data/', charts_views.get_data, name='get_data'),
    path('chart_data/', charts_views.ChartData.as_view(), name='chart_data')

    #path('home/', views.home)
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
