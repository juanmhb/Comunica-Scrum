from dataclasses import field
#import imp
from pyexpat import model
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from sqlparse import filters 

from .models import *
from Scrum.models import *

class MensajeForms(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields=['FechaHora','Proyecto','Descripcion']
        labels={
            'FechaHora':'Fecha y Hora (aaaa-mm-dd hh:mm)',
            'Proyecto':'Proyecto',
            'Descripcion':'Descripción'
        }

        widgets={
            #'Proyecto': forms.TextInput(
            #    attrs = {
            #        'class':'form-control',
            #        'placeholder':'Ingrese el Nombre del Proyecto'
            #    }
            #),
            'FechaHora': forms.DateInput(
                # format="%Y-%m-%d",
                attrs = {
                    'class':'form-control',
                    # 'type': 'date',
                    'class':'form-control',
                    'placeholder': 'Ejemplo: 2024-01-17 17:30'
                }
            ),
            'Descripcion': forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'rows':'3',
                    'placeholder': 'Ingrese la descripcion de este mensaje'
                }
            ),
        }

class UpdateMensajePDF_Forms(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields=['FechaHora','Proyecto','Descripcion', 'Status']
        labels={
            'FechaHora':'Fecha y Hora (aaaa-mm-dd hh:mm)',
            'Proyecto':'Proyecto',
            'Descripcion':'Descripción',
            'Status':'Status',
            # 'archivo':'Seleccione un archivo' # Obsoleto
        }

        widgets={
            #'Proyecto': forms.TextInput(
            #    attrs = {
            #        'class':'form-control',
            #        'placeholder':'Ingrese el Nombre del Proyecto'
            #    }
            #),
            'FechaHora': forms.DateInput(
                # format="%Y-%m-%d",
                format="%Y-%m-%d %H:%M",
                attrs = {
                    'class':'form-control',
                    # 'type': 'date',
                    'type': 'datetime-local',
                    'class':'form-control',
                    'placeholder': 'Ejemplo: 2024-01-17 17:30',
                }
            ),
            'Descripcion': forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'rows':'3',
                    'placeholder': 'Ingrese la descripcion de este mensaje'
                }
            ),
        }

class RefinamientoForms(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields=['FechaHora','Proyecto']
        labels={
            'FechaHora':'Fecha y Hora (aaaa-mm-dd hh:mm)',
            'Proyecto':'Proyecto',
        }

        widgets={
            #'Proyecto': forms.TextInput(
            #    attrs = {
            #        'class':'form-control',
            #        'placeholder':'Ingrese el Nombre del Proyecto'
            #    }
            #),
            'FechaHora': forms.DateInput(
                # format="%Y-%m-%d",
                attrs = {
                    'class':'form-control',
                    # 'type': 'date',
                    'class':'form-control',
                    'placeholder': 'Ejemplo: 2024-01-17 17:30'
                }
            ),
        }

class AsistentesForms(forms.ModelForm):
    class Meta:
        model = AsistentesEventosScrum
        fields=['Usuario','Rol','Status','TipoAsistencia']
        labels={
            'Usuario':'Usuario',
            'Rol':'Rol del usuario',
            'Status':'Estatus del usuario',
            'TipoAsistencia':'Tipo  de asistencia'
        }

        widgets={
            #'Proyecto': forms.TextInput(
            #    attrs = {
            #        'class':'form-control',
            #        'placeholder':'Ingrese el Nombre del Proyecto'
            #    }
            #),
        }

class AsistentesPlaneacion_Forms(forms.ModelForm):
    class Meta:
        model = AsistentesEventosScrum
        fields=['Status','TipoAsistencia']
        labels={
            'Status':'Status del usuario',
            'TipoAsistencia':'Tipo  de asistencia'
        }

        widgets={
            #'Proyecto': forms.TextInput(
            #    attrs = {
            #        'class':'form-control',
            #        'placeholder':'Ingrese el Nombre del Proyecto'
            #    }
            #),
        }

# Formulario BETA - para enviar mensajes
# No se ingresa informacion porque ya la recibe por id del Mensaje
class envAsistentesForms(forms.ModelForm):
    class Meta:
        model = AsistentesEventosScrum
        fields=[]
        labels={
            # 'Status':'Status del usuario',
        }

        widgets={
            #'Status': forms.TextInput(
            #    attrs = {
            #        'class':'form-control',
            #        'placeholder':'Ingrese el Nombre del Proyecto'
            #    }
            #),
        }

class EditarHistoriaUsuarioBL_Forms(forms.ModelForm):
    class Meta:
        model = HistoriaUsuario
        fields=['Estatus','nombre','ultimaactualizacion','descripcion','HorasEstimadas','Prioridad',
                'CriteriosAceptacion','tereasasignadas','Sprint']
        labels={
            'Estatus':'Estatus',
            'nombre':'Nombre de la historia de usuario',
            'ultimaactualizacion':'Fecha de ultima actualizacion (aaaa-mm-dd)',
            'descripcion':'Descripción de la historia de usuario',
            'HorasEstimadas':'Horas estimadas',
            'Prioridad':'Prioridad',
            'CriteriosAceptacion':'Criterios de aceptación',
            'tereasasignadas':'Tareas asignadas',
            'Sprint':'Sprint'
        }

        widgets={
            'ultimaactualizacion': forms.DateInput(
                format="%Y-%m-%d",
                attrs = {
                    # 'class':'form-control',
                    'type': 'date',
                    'placeholder': 'Ejemplo: 2024-01-17 17:30'
                }
            ),
        }

# Formulario general
class Archivos_forms(forms.ModelForm):
    class Meta:
        model = m_Archivos
        fields=['Descripcion','Archivo','Mensaje','Proyecto']
        labels={
            'Descripcion':'Nombre del archivo',
            'Archivo':'Archivo',
        }

        widgets={
            'Descripcion': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder': 'Nombre del archivo'
                }
            ),
        }

# Formulario con id, herendando 2 atributos
class ArchivosID_forms(forms.ModelForm):
    class Meta:
        model = m_Archivos
        fields=['Descripcion','Archivo']
        labels={
            'Descripcion':'Nombre del archivo',
            'Archivo':'Archivo',
        }

        widgets={
            'Descripcion': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder': 'Nombre del archivo'
                }
            ),
        }

# Mensaje de Retroalimenacion product owner
class retroAlimentacionBL_Forms(forms.ModelForm):
    class Meta:
        model = MensajeRetroA
        fields=['Contestacion']
        labels={
            'Contestacion':'Contestación',
            'Status':'Estatus'
        }

        widgets={
            'Contestacion': forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'placeholder': 'Escriba su respuesta'
                }
            ),
        }

# Mensaje de Retroalimenacion, empleada y scrum master
class retroAlimentacion_Forms(forms.ModelForm):
    class Meta:
        model = MensajeRetroA
        fields=['Descripcion']
        labels={
            'Descripcion':'Descripción',
            # 'Contestacion':'Contestación',
            # 'Status':'Estatus'
        }

        widgets={
            'Descripcion': forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'placeholder': 'Descripción general'
                }
            ),
            #'Contestacion': forms.Textarea(
            #    attrs = {
            #        'class':'form-control',
            #        'placeholder': 'Escriba su respuesta'
            #    }
            #),
        }

# ----------------- Reunion Diaria --------------------
class reunionDiaria_Forms(forms.ModelForm):
    class Meta:
        model = m_ReunionDiaria
        fields=['ObstaculosPresentados','PlanDiaSiguiente','TrabajoRealizadoDiaAnterior']
        labels={
            'ObstaculosPresentados':'Obstaculos presentados',
            'PlanDiaSiguiente':'Planificación del siguiente día',
            'TrabajoRealizadoDiaAnterior':'Trabajo realizado el día anterior'
        }

        widgets={
            'TrabajoRealizadoDiaAnterior': forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'placeholder': 'Es la descripción de lo realizado el día anterior por el desarrollador'
                }
          ),
          'ObstaculosPresentados': forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'placeholder': 'Es la descripción de los obstáculos presentados durante el día de trabajo por el desarrollador'
                }
          ),
          'PlanDiaSiguiente': forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'placeholder': 'Es la descripción de lo que va hacer el desarrollador el siguiente día de trabajo'
                }
          ),
        }

# --------------- Reunion planeacion sprint
class reunionPlaneacionSprint_Forms(forms.ModelForm):
    class Meta:
        # model = m_PlanificacionSprint
        model = Mensaje
        fields=['FechaHora','Descripcion','Proyecto','Sprint']
        labels={
            'FechaHora':'Fecha y hora',
            'Descripcion':'Descripción',
            'Proyecto':'Proyecto',
            'Sprint': 'Sprint',
            # 'archivo':'Archivo (opcional)'
        }

        widgets={
            'FechaHora': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'FechaHora': 'Ejemplo: 2024-01-17 17:30'
                }
            ),
            'Descripcion': forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'rows':'3',
                    'placeholder': 'Ingrese la descripcion de este mensaje'
                }
            ),

        }

class MensajePlaneacionForms(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields=['FechaHora','Proyecto','Descripcion','Sprint']
        labels={
            'FechaHora':'Fecha y Hora (aaaa-mm-dd hh:mm)',
            'Proyecto':'Proyecto',
            'Descripcion':'Descripción',
            'Sprint':'Sprint'
        }

        widgets={
            #'Proyecto': forms.TextInput(
            #    attrs = {
            #        'class':'form-control',
            #        'placeholder':'Ingrese el Nombre del Proyecto'
            #    }
            #),
            'FechaHora': forms.DateInput(
                # format="%Y-%m-%d",
                attrs = {
                    'class':'form-control',
                    # 'type': 'date',
                    'class':'form-control',
                    'placeholder': 'Ejemplo: 2024-01-17 17:30'
                }
            ),
            'Descripcion': forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'rows':'3',
                    'placeholder': 'Ingrese la descripcion de este mensaje'
                }
            ),
        }

# Opcion 2, herenado datos de Sprint
class MensajePlaneacionSprintForms(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields=['FechaHora']
        labels={
            'FechaHora':'Fecha y Hora (aaaa-mm-dd hh:mm)',
        }

        widgets={
            #'Proyecto': forms.TextInput(
            #    attrs = {
            #        'class':'form-control',
            #        'placeholder':'Ingrese el Nombre del Proyecto'
            #    }
            #),
            'FechaHora': forms.DateInput(
                # format="%Y-%m-%d",
                attrs = {
                    'class':'form-control',
                    # 'type': 'date',
                    'class':'form-control',
                    'placeholder': 'Ejemplo: 2024-01-17 17:30'
                }
            ),
        }

# Reunion de revision del sprint
class MensajeRevisionSprintForms(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields=['FechaHora']
        labels={
            'FechaHora':'Fecha y Hora (aaaa-mm-dd hh:mm)',
        }

        widgets={
            #'Proyecto': forms.TextInput(
            #    attrs = {
            #        'class':'form-control',
            #        'placeholder':'Ingrese el Nombre del Proyecto'
            #    }
            #),
            'FechaHora': forms.DateInput(
                # format="%Y-%m-%d",
                attrs = {
                    'class':'form-control',
                    # 'type': 'date',
                    'class':'form-control',
                    'placeholder': 'Ejemplo: 2024-01-17 17:30'
                }
            ),
        }

# Formulario para comentarios de los asistentes
class comentarios_Forms(forms.ModelForm):
    class Meta:
        model = m_Comentarios
        fields=['Comentarios']
        labels={
            'Comentarios':'Comentarios'
        }

        widgets={
            'Comentarios': forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'rows':'3',
                    'placeholder': 'Escriba su comentario'
                }
            ),

        }

# Formulario para la reunion de retrospectiva del sprint
class comentariosRetrospectiva_Forms(forms.ModelForm):
    class Meta:
        model = m_RetrospectivaSprint
        fields=['Comentarios','OportunidadesMejora']
        labels={
            'Comentarios':'Reflexiones/Comentarios:',
            'OportunidadesMejora':'Oportunidades de mejora'
        }

        widgets={
            'Comentarios': forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'rows':'3',
                    'placeholder': 'Escriba su comentario'
                }
            ),
            'OportunidadesMejora': forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'rows':'3',
                    'placeholder': 'Escriba su comentario'
                }
            ),

        }