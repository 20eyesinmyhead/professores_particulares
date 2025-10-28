"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # MODIFICAÇÃO 1: Redireciona a raiz do site ('') para o app 'users'
    # path('professores/', include('users.urls', namespace='users')), # REMOVA/COMENTE ESTA LINHA
    path('', include('users.urls', namespace='users')), # <-- SUBSTITUA PELA RAIZ

    # MODIFICAÇÃO 2: Se você quiser manter a URL /professores/ (opcional, mas recomendado para navegação)
    # path('professores/', include('users.urls', namespace='users')),
]