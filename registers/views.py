from unicodedata import category
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from requests import RequestException
from .models import *
from django.urls import reverse
from django.shortcuts import render
from docxtpl import DocxTemplate
import io
#MANEJO DE FECHAS
from datetime import date

#Manejo de encriptado
from django.contrib.auth.hashers import make_password, check_password

#LIBRERIAS PARA GENERAR PDFS
import os
from django.conf import settings
from django.template import Context
from django.template.loader import get_template
from xhtml2pdf import pisa

# Create your views here.
def index(request):
    return render(request, "registers/index.html")

def principal(request):
    try:
        selected_user = User.objects.get(username=request.POST["usuario"])
    except (KeyError, User.DoesNotExist):
        return render(request, "registers/index.html",{
            "error":"El usuario no existe",
        })
    else:
        if check_password(request.POST["password"], selected_user.password) :
            request.session['id'] = selected_user.id
            palabras = selected_user.name.split()
            categorias = Category.objects.filter(description=selected_user.superuser)
            nueva_cadena = ""
            for p in palabras:
                nueva_cadena = nueva_cadena + p[0]
            nueva_cadena=nueva_cadena.upper()
            return render(request, "registers/principal.html", {
                "iniciales":nueva_cadena,
                "uservalues":selected_user,
                'categorias':categorias,
            })
        else:
            return render(request, "registers/index.html",{
                "error":"El password es incorrecto",
            })
    
def ticket(request, id, id_cat):
    try:
        id_user = request.session['id']
        categoria = Category.objects.get(pk=id_cat)
        selected_user = User.objects.get(pk=id_user)
        categorias = Category.objects.filter(description=selected_user.superuser)
        palabras = selected_user.name.split()
        nueva_cadena = ""
        for p in palabras:
            nueva_cadena = nueva_cadena + p[0]
        nueva_cadena=nueva_cadena.upper()
        return render(request, "registers/ticket.html",{
            "iniciales":nueva_cadena,
            "uservalues":selected_user,
            "categoria":categoria,
            "categorias":categorias,
            "check":"asig",
        })
    except (KeyError, User.DoesNotExist):
        return render(request, "registers/index.html",{
            "error_message":"Debe Loguearse",
        })

def ticketasig(request, id, report_id):
    try:
        id_user = request.session['id']
    except (KeyError, User.DoesNotExist):
        return render(request, "registers/index.html",{
            "error_message":"Debe Loguearse",
        })
    else:
        report= Report.objects.get(pk=report_id)
        selected_user = User.objects.get(pk=id)
        palabras = selected_user.name.split()
        nueva_cadena = ""
        for p in palabras:
            nueva_cadena = nueva_cadena + p[0]
        nueva_cadena=nueva_cadena.upper()
        categoria = Category.objects.get(name_category=report.category)
        categorias = Category.objects.filter(description=selected_user.superuser)
        return render(request, "registers/ticket.html",{
            "iniciales":nueva_cadena,
            "uservalues":selected_user,
            "reportvalues":report,
            "categoria": categoria,
            "categorias": categorias,
        })


#Se encarga del trabajo grueso de guardar el reporte
def regtick(request, id, id_cat):
    try:
        id_user = request.session['id']
    except (KeyError, User.DoesNotExist):
        return render(request, "registers/index.html",{
            "error_message":"Debe Loguearse",
        })
    else:
        if request.POST["enviar"]=="Asignar":
            categoria = Category.objects.get(name_category=request.POST["cate"])
            para = request.POST["destinatario"]
            asunto = request.POST["asunto"]
            fecha = timezone.now()
            report = Report.objects.filter(category_id=categoria.id)
            t = len(report)
            if t>0 and report[t-1].pub_date.year == timezone.now().year:
                new_number = report[t-1].number + 1
            else:
                new_number = 1
            new_report = Report(topic=asunto,to=para,pub_date=fecha,category_id=categoria.id,super_user_id=1, user_id=id, number=new_number)
            new_report.save()
            selected_user = User.objects.get(pk=id)
            return HttpResponseRedirect(reverse("registers:ticketasig", args=(id, new_report.id,)))
        else:
            categoria = Category.objects.get(pk=id_cat)
            selected_user = User.objects.get(pk=id_user)
            categorias = Category.objects.filter(description=selected_user.superuser)
            palabras = selected_user.name.split()
            nueva_cadena = ""
            for p in palabras:
                nueva_cadena = nueva_cadena + p[0]
            nueva_cadena=nueva_cadena.upper()
            return render(request, "registers/ticket.html",{
                "iniciales":nueva_cadena,
                "uservalues":selected_user,
                "categoria":categoria,
                "categorias":categorias,
                "check":"asig",
            })

#Pestaña de registros
def registro(request, id):
    try:
        id_user = request.session['id']
    except (KeyError):
        return render(request, "registers/index.html",{
            "error_message":"Debe Loguearse",
        })
    else:
        selected_user = User.objects.get(pk=id)
        categorias = Category.objects.filter(description=selected_user.superuser)
        users = User.objects.all()
        palabras = selected_user.name.split()
        nueva_cadena = ""
        for p in palabras:
            nueva_cadena = nueva_cadena + p[0]
        nueva_cadena=nueva_cadena.upper()
        return render(request, "registers/registro.html",{
            "iniciales":nueva_cadena,
            "uservalues":selected_user,
            "categorias":categorias,
            "users":users,
        })

#Trabajo de busqueda en la bd
def buscador(request, id):
    try:
        id_user = request.session['id']
    except (KeyError):
        return render(request, "registers/index.html",{
            "error_message":"Debe Loguearse",
        })
    else:
        selected_user = User.objects.get(pk=id)
        palabras = selected_user.name.split()
        nueva_cadena = ""
        for p in palabras:
            nueva_cadena = nueva_cadena + p[0]
        nueva_cadena=nueva_cadena.upper()
        reportes = Report.objects.all()
        if request.POST["nro"] != "":
            reportes = reportes.filter(number=request.POST["nro"])
        #fecha ini
        if request.POST["fecha_ini"] !="":
            reportes = reportes.filter(pub_date__range=[request.POST["fecha_ini"], date.today()])
        #fecha fin
        if request.POST["fecha_fin"] !="":
            reportes = reportes.filter(pub_date__range=["2019-01-01",request.POST["fecha_ini"]])
        if request.POST["categoria"] != "":
            select_category = Category.objects.get(name_category=request.POST["categoria"])
            reportes = reportes.filter(category_id=select_category.id)
        if request.POST["responsable"] != "":
            select_user = User.objects.get(name=request.POST["responsable"])
            reportes = reportes.filter(user_id=select_user.id)
        if request.POST["destinatario"] != "":
            reportes = reportes.filter(to__contains=request.POST["destinatario"])
        if request.POST["asunto"] != "":
            reportes = reportes.filter(topic__contains=request.POST["asunto"])
        
        reportes_general = reportes.order_by('category','number')

        document = Document.objects.all()
        document = document.order_by('category','numero')


        categorias = Category.objects.filter(description=selected_user.superuser)
        usuarios = User.objects.all()
        reportes_elegidos = {}
        for reporte in reportes_general:
            t=len(document.filter(dateTimeOfUpload__year=reporte.pub_date.year).filter(numero=reporte.number))
            if t>0:
                reportes_elegidos[str(reporte.id)]={'number':reporte.number, 'pub_date':str(reporte.pub_date.year)+'/'+str(reporte.pub_date.month)+'/'+str(reporte.pub_date.day), 'categoria':Category.objects.get(pk=reporte.category_id).name_category, 'responsable':User.objects.get(pk=reporte.user_id).name, 'destinatario':reporte.to, 'asunto':reporte.topic, 'url':document.filter(dateTimeOfUpload__year=reporte.pub_date.year).filter(numero=reporte.number).latest('numero')}
            else:
                reportes_elegidos[str(reporte.id)]={'number':reporte.number, 'pub_date':str(reporte.pub_date.year)+'/'+str(reporte.pub_date.month)+'/'+str(reporte.pub_date.day), 'categoria':Category.objects.get(pk=reporte.category_id).name_category, 'responsable':User.objects.get(pk=reporte.user_id).name, 'destinatario':reporte.to, 'asunto':reporte.topic}
            
        if request.POST["enviar"] == "buscar":
            return render(request, "registers/registro.html",{
                "iniciales":nueva_cadena,
                "uservalues":selected_user,
                "reporteseleg": reportes_elegidos,
                "doc":document, 
                "categorias": categorias,
                "users": usuarios,
            })
        else:
            
            try:
                template = get_template('registers/registro_pdf.html')
                context= {
                    "reporteseleg":reportes_elegidos,
                }
                html = template.render(context)
                response = HttpResponse(content_type='application/pdf')
                #response['Content-Disposition'] = 'attachment; filename="report.pdf"'
                #response['Content-Disposition'] = 'attachment; filename="report.pdf"'
                pisaStatus = pisa.CreatePDF(
                    html, dest=response
                )
                
                if pisaStatus.err:
                    return HttpResponse("We had errors <pre>"+html+'</pre>')
                return response
            except: 
                pass
            return HttpResponse('registers: principal')

def close(request):
    del request.session['id']
    return HttpResponseRedirect(reverse("registers:index", args=()))

def config(request, id):
    try:
        id_user = request.session['id']
    except (KeyError):
        return render(request, "registers/index.html",{
            "error_message":"Debe Loguearse",
        })
    else:
        selected_user = User.objects.get(pk=id)
        categorias = Category.objects.filter(description=selected_user.superuser)
        palabras = selected_user.name.split()
        nueva_cadena = ""
        for p in palabras:
            nueva_cadena = nueva_cadena + p[0]
        nueva_cadena=nueva_cadena.upper()
        return render(request, "registers/usuario.html",{
            "uservalues":selected_user,
            "iniciales":nueva_cadena,
            "categorias": categorias,
        })

def cambio_password(request, id):
    try:
        id_user = request.session['id']
    except (KeyError):
        return render(request, "registers/index.html",{
            "error_message":"Debe Loguearse",
        })
    else:
        selected_user = User.objects.get(pk=id)
        palabras = selected_user.name.split()
        categorias = Category.objects.filter(description=selected_user.superuser)
        nueva_cadena=""
        for p in palabras:
            nueva_cadena = nueva_cadena + p[0]
        nueva_cadena=nueva_cadena.upper()
        password=make_password(request.POST["clave"])
        selected_user.password=password
        selected_user.save()
        return render(request, "registers/usuario.html",{
            "uservalues":selected_user,
            "iniciales":nueva_cadena,
            "categorias": categorias,
        })
def upload(request):
    try:
        id_user = request.session['id']
    except (KeyError):
        return render(request, "registers/index.html",{
            "error_message":"Debe Loguearse",
        })
    else:
        selected_user = User.objects.get(pk=id_user)
        categorias = Category.objects.filter(description=selected_user.superuser)
        palabras = selected_user.name.split()
        nueva_cadena=""
        for p in palabras:
            nueva_cadena = nueva_cadena + p[0]
        nueva_cadena=nueva_cadena.upper()
        return render(request, "registers/upload-file.html", context={
            "uservalues":selected_user,
            "iniciales":nueva_cadena,
            "categorias": categorias,
        })
def save(request):
    try:
        id_user = request.session['id']
    except (KeyError):
        return render(request, "registers/index.html",{
            "error_message":"Debe Loguearse",
        })
    else:
        selected_user = User.objects.get(pk=id_user)
        categorias = Category.objects.filter(description=selected_user.superuser)
        palabras = selected_user.name.split()
        nueva_cadena=""
        for p in palabras:
            nueva_cadena = nueva_cadena + p[0]
        nueva_cadena=nueva_cadena.upper()
        return render(request, "registers/upload-file.html", context={
            "files": "documento agregado",
            "uservalues":selected_user,
            "iniciales":nueva_cadena,
            "categorias": categorias,
        })

def uploadFile(request):
    try:
        id_user = request.session['id']
    except (KeyError):
        return render(request, "registers/index.html",{
            "error_message":"Debe Loguearse",
        })
    else:
        if request.method == "POST":
            try:
                # Fetching the form data
                number = request.POST["numero"]
                categoria = Category.objects.get(name_category=request.POST["categoria"])
                uploadedFile = request.FILES["archivo"]
                report = Report.objects.filter(pub_date__year=request.POST["año"]).filter(category=categoria.id).get(number=number)
                fecha = report.pub_date
            except (Report.DoesNotExist, KeyError):
                selected_user = User.objects.get(pk=id_user)
                categorias = Category.objects.filter(description=selected_user.superuser)
                palabras = selected_user.name.split()
                nueva_cadena=""
                for p in palabras:
                    nueva_cadena = nueva_cadena + p[0]
                nueva_cadena=nueva_cadena.upper()
                return render(request, "registers/upload-file.html", context={
                    "files": "El correlativos no existe en la base de datos",
                    "uservalues":selected_user,
                    "iniciales":nueva_cadena,
                    "categorias": categorias,
                })
            else:
                document = Document(
		numero = number,
                category = categoria,
                uploadedFile = uploadedFile,
               	dateTimeOfUpload = fecha
                )
                document.save()
                return HttpResponseRedirect(reverse("registers:save", args=()))
#Reseteo de contraseña predefinida
def reset(request):
    return render(request, "registers/reset.html")

def resetpass(request):
    try:
        selected_user = User.objects.get(username=request.POST["usuario"])
    except (KeyError, User.DoesNotExist):
        return render(request, "registers/reset.html",{
            "error":"El usuario no existe",
        })
    else:
        if request.POST["password"] == selected_user.password :
            request.session['id'] = selected_user.id
            palabras = selected_user.name.split()
            nueva_cadena = ""
            for p in palabras:
                nueva_cadena = nueva_cadena + p[0]
            nueva_cadena=nueva_cadena.upper()
            return render(request, "registers/usuario.html", {
                "uservalues":selected_user,
            })
        else:
            return render(request, "registers/index.html",{
                "error":"El password es incorrecto",
            })

def crearcom(request, idcorrelativo):
    MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    id_user = request.session['id']
    val = Report.objects.get(pk=idcorrelativo)
    username = User.objects.get(pk=id_user)
    palabras = username.name.split()
    nueva_cadena = ""
    for p in palabras:
        nueva_cadena = nueva_cadena + p[0]
    iniciales=nueva_cadena.upper()
    name = val.category
    parametros = {
        'numero': str(val.number),
        'dia': str(val.pub_date.day),
        'mes': val.pub_date.month,
        'anio': str(val.pub_date.year),
        'usuario':username.username,
        'iniciales':iniciales,
    }
    doctlp = DocxTemplate(str(settings.BASE_DIR) +name.file.url)
    context = {
            'numero_anio': parametros['numero']+"/"+parametros['anio'],
            'numero': str(val.number),
            'dia': parametros['dia'],
            'mes':MESES[parametros['mes']-1],
            'anio':parametros['anio'],
            'usuario':parametros['usuario'],
            'iniciales':iniciales,
    }
    doctlp.render(context)
    nombre_doc = val.category.name_category+"_"+parametros['numero']+"-"+parametros['anio']+'.docx'
        
        #doctlp.save('media/outputs/'+nombre_doc)
    document_data = io.BytesIO()
    doctlp.save(document_data)
    document_data.seek(0)
    response = HttpResponse(
        document_data.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    response["Content-Disposition"] = f'attachment; filename = {nombre_doc}'
    response["Content-Encoding"] = "UTF-8"
    return response
