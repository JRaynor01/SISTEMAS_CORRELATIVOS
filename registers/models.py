from django.db import models
import os 
from django.conf import settings

def models_directory_path_file(instance, filename):
    path_file = 'modelos/{0}.docx'.format(instance.name_category)
    full_path = os.path.join(settings.MEDIA_ROOT, path_file)
    
    if os.path.exists(full_path):
        os.remove(full_path)
        
    return path_file
     
#DATA BASE SISTEMA CORRELATIVOS

class Super_user(models.Model):
    username = models.CharField(max_length=30)
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=20)
    firm = models.CharField(max_length=10)

    def __str__(self):
        return f'{self.username}: -> {self.name}'

class User(models.Model):
    username = models.CharField(max_length=30)
    name = models.CharField(max_length=30)
    password = models.CharField(max_length=200)
    superuser = models.CharField(max_length=20, default="")
    value = models.CharField(max_length=20, default="")

    def __str__(self):
        return f'usuario: {self.name}'

class Category(models.Model):
    name_category = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    file = models.FileField(upload_to=models_directory_path_file, blank=True)

    def __str__(self):
        return f'{self.name_category}'

class Report(models.Model): #iddefinido automatico por python
    topic = models.CharField(max_length=200) #asunto
    to= models.CharField(max_length=200) # dirigido a
    user = models.ForeignKey(User, on_delete=models.CASCADE) #usuario que solicita 
    super_user = models.ForeignKey(Super_user, on_delete=models.DO_NOTHING) #superusuaior que aprueba esto
    category = models.ForeignKey(Category, on_delete=models.CASCADE) #categoria ala que pertenece
    pub_date = models.DateField(auto_now=False) #fecha de solicitud
    number = models.IntegerField() #nuemrodel reporte

    def __str__(self):
        return f'{self.number} {self.category} {self.pub_date}'

class Document(models.Model):
    numero = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1) #categoria ala que pertenece
    uploadedFile = models.FileField(upload_to = 'DocumentosCargados')
    dateTimeOfUpload = models.DateTimeField(auto_now = True)
