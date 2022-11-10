from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "registers"
urlpatterns =[
    path("", views.index, name="index"),
    path("principal/", views.principal, name="principal"),
    path("<int:id>/registros/", views.registro, name="registro"),
    path("close/", views.close, name="close"),

    #path("<int:uservalue.id>/ticket")
    path("<int:id>/<int:id_cat>/ticket", views.ticket, name="ticket"),
    path("<int:id>/<int:id_cat>/regtick/", views.regtick, name="regtick"),
    path("<int:id>/<int:report_id>/tickasig/", views.ticketasig, name="ticketasig"),
    path("<int:id>/buscador", views.buscador, name="buscador"),
    path("<int:id>/config", views.config, name ="config"),
    path("<int:id>/change", views.cambio_password, name ="change"),

    #subida de pdfs administradores
    path("upload/", views.upload, name="upload"),
    path("uploadFile/", views.uploadFile, name="uploadFile"),
    path("save/", views.save, name="save"),

    #menu de recuperacion de contraseña
    path("reset/", views.reset, name="resetpassword"),
    path("reset/change_password", views.resetpass, name="resetpass"),
    
    #visualizacion de pdfs
     #Crear Automaticamente
    path("documentos/<int:idcorrelativo>/", views.crearcom , name="creardoc")
]
if settings.DEBUG: 
    urlpatterns += static(
        settings.MEDIA_URL, 
        document_root = settings.MEDIA_ROOT
    )
