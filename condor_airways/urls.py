from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from aerolinea.views import CustomLoginView
from aerolinea import views

# Redirigir /admin/ al dashboard del root si es root
def redirect_root_admin(request):
    if request.user.is_authenticated and hasattr(request.user,"usuario"):
        if request.user.usuario.es_root:
            return redirect("root_dashboard")
        elif request.user.usuario.es_admin:
            return redirect("admin_dashboard")
        return redirect("/accounts/login/")

urlpatterns = [
    path('admin/logout/', views.cerrar_sesion, name='admin_logout'),
    path('admin/', redirect_root_admin, name='redirect_root_admin'),
    #path('admin/',admin.site.urls),
    path('', lambda request: redirect('buscar_vuelos')),
    path('', include("aerolinea.urls")), 
    path('accounts/login/', CustomLoginView.as_view(), name='login'),    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)