from dataclasses import field
#import imp
from pyexpat import model
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from sqlparse import filters 
import datetime
from .models import *


class CustomUserCreationForm(UserCreationForm):
    class Meta :
        model = User
        fields = ['username', "first_name", "last_name", "email", "password1", "password2"]
        labels = {
            'last_name': 'Apellidos'
        } 

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields=['rfc','telefono','cedulaprofesional','Pais','Idioma']
        labels={
            'rfc':'Rfc',
            'telefono':'Teléfono',
            'cedulaprofesional':'Cédula Profesional',
        }

        widgets={
            'rfc': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese el RFC'
                }
            ),
            'telefono': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese el teléfono'
                }
            ),
            'cedulaprofesional': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese la Cédula Profesional'
                }
            ),
            'País': forms.Select(
                attrs = {
                    'class':'form-control',
                    'placeholder': 'Ingrese el País'
                }
            ),
            'Idioma': forms.Select(
                attrs = {
                    'class':'form-control',
                    'placeholder': 'Ingrese el Idioma'
                }
            ),
        }


class ProductBacklogForm(forms.ModelForm):
    class Meta:
        model = HistoriaUsuario
        fields = ['fechacreacion', 'ultimaactualizacion']
        labels = {
            'fechacreacion': 'Fecha de creación',
            'ultimaactualizacion': 'Última actualización'
        }
        widgets = {
            'fechacreacion': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese la fecha de creación'
                }
            ),
            'ultimaactualizacion': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese la última actualización'
                }
            ),
        }

class DateInput(forms.DateInput):
    input_type = 'date'

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields=['nombreproyecto','fechainicio','fechafinal','objetivo','impacto','homologacionvision']
        labels={
            # 'JefeProyecto':'Jefe Proyeto',
            'nombreproyecto':'Nombre de Proyecto',
            'fechainicio':'Fecha de Inicio',
            'fechafinal':'Fecha de Conclusión',
            'objetivo':'Objetivo',
            'impacto':'Impacto',
            'homologacionvision':'Homologacion de la Visión'
        }

        widgets={
            # 'JefeProyecto':forms.Select(
            #     attrs = {
            #         'class':'form-control',
            #         'placeholder':'Ingrese el Nombre del Jefe de Proyecto'
            #     }
            # ),
            'nombreproyecto': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese el Nombre del Proyecto'
                }
            ),
            'fechainicio': DateInput(
                format="%Y-%m-%d",
                attrs = {
                    'class':'form-control',
                    'type': 'date',
                }
            ),
            'fechafinal': DateInput(
                format="%Y-%m-%d",
                attrs = {
                    'class':'form-control',
                    'type': 'date',
                }
            ),
            'objetivo': forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'rows':'3',
                    'placeholder': 'Ingrese el Objetivo'
                }
            ),
            'impacto': forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'rows':'3',
                    'placeholder': 'Ingrese el Impacto'
                }
            ),
            'homologacionvision': forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'rows':'5',
                    'placeholder': 'Ingrese la Homologación de la Vision'
                }
            ),
        }



class HistoriaUsuarioForm(forms.ModelForm):
    class Meta:
        model = HistoriaUsuario
        fields = ['nombre','fechacreacion','ultimaactualizacion','descripcion', 'HorasEstimadas', 'Prioridad', 'CriteriosAceptacion']
        labels = {
            'nombre':'Nombre',
            'fechacreacion':'Fecha de creación',
            'ultimaactualizacion':'Fecha de actualización',
            'descripcion':'Descripción',
            'HorasEstimadas':'Horas Estimadas',
            'Prioridad' :'Prioridad',
            'CriteriosAceptacion': 'Criterios de Aceptación'

        }
        widgets={
            # 'ProductBacklog': forms.Select(
            #     attrs = {
            #         'class':'form-control',
            #         'placeholder':'Seleccionar proyecto'
            #     }
            # ),
            # 'Estatus': forms.Select(
            #     attrs = {
            #         'class':'form-control',
            #         'placeholder':'Seleccionar estatus'
            #     }
            # ),
            'nombre': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese nombre'
                }
            ),
            'fechacreacion': DateInput(
                format="%Y-%m-%d",
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese fecha de creación'
                }
            ),
             'ultimaactualizacion': DateInput(
                 format="%Y-%m-%d",
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese ultima fecha de actualización'
                }
            ),
            'descripcion': forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'rows':'3',
                    'placeholder': 'Ingrese una descripción'
                }
            ),
            'HorasEstimadas': forms.NumberInput(
                attrs = {
                    'class':'form-control',
                    'placeholder': 'Ingrese las horas estimadas'
                }
            ),
            # 'Prioridad': forms.NumberInput(
            #     attrs = {
            #         'class':'form-control',
            #         'placeholder': 'Ingrese la Prioridad (1-5)'
            #     }
            # ),
            'CriteriosAceptacion': forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'rows':'3',
                    'placeholder': 'Ingrese los Criterios de Aceptación'
                }
            ),
        }



class SprintForm(forms.ModelForm):
    class Meta:
        model = Sprint
        fields = ['nombresprint','fechainiciosprint','fechafinalsprint','numerosprint','objetivosprint']
        labels = {
            'nombresprint':'Nombre',
            'fechainiciosprint':'Fecha de Inicio',
            'fechafinalsprint':'Fecha de Finalización',
            'numerosprint':'Número de Sprint',
            'objetivosprint':'Objetivo de Sprint'
        }
        widgets={
            'nombresprint': forms.TextInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese nombre'
                }
            ),
            'fechainiciosprint': DateInput(
                format="%Y-%m-%d",
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese fecha de inicio'
                }
            ),
             'fechafinalsprint': DateInput(
                format="%Y-%m-%d",
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese fecha de finalización '
                }
            ),
            'numerosprint': forms.NumberInput(
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese número de Sprint '
                }
            ),
            'objetivosprint': forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'rows':'3',
                    'placeholder': 'Ingrese un objetivo'
                }
            ),
        }


class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['nombre', 'Rol', 'Prioridad', 'fechainicioplaneado', 'fechafinalplaneado', 'horasestimadas', 'Empleado']
        labels = {
            'nombre': 'Nombre',
            'Rol': 'Rol del Participante',
            'fechainicioplaneado': 'Fecha de inicio planeado',
            'Prioridad': 'Nivel de prioridad',
            'fechafinalplaneado': 'Fecha de terminación planeada',
            'horasestimadas': 'Horas estimadas',
            'Empleado': 'Seleccionar Empleados',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese nombre'}),
            'Rol': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Seleccione la clasificación'}),
            'Prioridad': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Seleccione el nivel de prioridad'}),
            'fechainicioplaneado': DateInput(format="%Y-%m-%d",attrs = {'class':'form-control','placeholder':'Ingrese fecha de inicio planeada'}),
            'fechafinalplaneado': DateInput(format="%Y-%m-%d",attrs = {'class':'form-control','placeholder':'Ingrese fecha final planeada'}),
            'horasestimadas': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese horas estimadas'}),
            'Empleado': forms.Select(attrs={'class': 'form-control'}),
        }










class TareaAvanceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        self.dias_habiles = []
        self.dias_asociados = []
        self.lista_dias_horas = []  # Hacer lista_dias_horas un atributo de la instancia
        sprint = instance.tarea.HistoriaUsuario.Sprint if instance else None

        if sprint:
            fechainicio = sprint.fechainiciosprint
            fechafin = sprint.fechafinalsprint or datetime.date.today()
            delta = fechafin - fechainicio

            # Filtrar los días no laborales (sábados y domingos)
            self.dias_habiles = [
                fechainicio + datetime.timedelta(days=i) for i in range(delta.days + 1)
                if (fechainicio + datetime.timedelta(days=i)).weekday() < 5
            ]

            self.dias_asociados = [
                (f'dia_{self.dias_habiles[i-1].day}', getattr(instance, f'dia_{self.dias_habiles[i-1].day}', '0/0')) for i in range(1, len(self.dias_habiles) + 1)
                if getattr(instance, f'dia_{self.dias_habiles[i-1].day}', None)
            ]

            
            # Añadir campo 'horasReales' si no está en los campos
            if 'horasReales' not in self.fields:
                self.fields['horasReales'] = forms.CharField(
                    label='Horas reales',
                    initial=instance.horasReales if instance else '',
                    max_length=5,
                    required=False,
                    widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese horas reales'})
                )
            #Oculta TODOS los campos de los días de captura
            for i in range(1, 32): # del 1 al 31, el 32 no se considera
                self.fields[f'dia_{i}'].widget = forms.HiddenInput()

            # Añadir campos para cada día 
            for i, dia in enumerate(self.dias_habiles, start=1):
                field_name = f'dia_{dia.day}'
                valor = getattr(instance, field_name, '0/0')
                label = f'Día {dia.strftime("%d/%m/%Y")}'
                self.fields[field_name] = forms.CharField(
                    label=label,
                    initial=valor,
                    max_length=5,
                    required=False,
                    widget=forms.TextInput( #Muestra los campos de los días que correspondan para su captura, antes estaban ocultos
                        attrs={'class': 'form-control', 'disabled': 'disabled'} if dia.weekday() >= 5 else {'class': 'form-control'}
                    )
                )
    def clean(self):
        cleaned_data = super().clean()
        horas_dedicadas = 0
        horas_reales = 0
        for i, dia in enumerate(self.dias_habiles, start=1):
            if dia.weekday() < 5:  # Solo procesar días laborales
                field_name = f'dia_{dia.day}'
                valor = cleaned_data.get(field_name, '0/0')
                if valor:
                    try:
                        horas_dedicadas_dia, horas_restantes = map(int, valor.split('/'))
                        horas_reales += horas_dedicadas_dia
                       # horas_dedicadas += horas_dedicadas_dia
                    except ValueError:
                        self.add_error(field_name, "Formato de valor no válido. Debe ser 'n/m'.")
                            # Añadir la tupla a la lista
                    self.lista_dias_horas.append((dia, horas_dedicadas_dia, horas_restantes))
        cleaned_data['horasReales'] = horas_reales
        cleaned_data['horasDedicadas'] = cleaned_data.get('horasDedicadas', 0)
        cleaned_data['lista_dias_horas'] = self.lista_dias_horas

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Actualiza los campos de horasDedicadas y horasRestantes basados en los datos limpios
        if commit:
            instance.horasDedicadas = self.cleaned_data.get('horasDedicadas', 0)
            instance.horasReales = self.cleaned_data.get('horasReales', 0)
            # Calcula las horas restantes
            horas_dedicadas = instance.horasDedicadas
            horas_restantes = instance.horasRestantes if instance.horasRestantes else 0
            horas_reales = instance.horasReales 
            instance.horasRestantes = max(horas_restantes - horas_reales, 0)
            
            # Actualiza los campos de los días
            for i in range(1, len(self.dias_habiles) + 1):
                #field_name = f'dia_{i}'
                field_name = f'dia_{self.dias_habiles[i-1].day}'
                setattr(instance, field_name, self.cleaned_data.get(field_name, '0/0'))
            instance.save()
        return instance

    class Meta:
        model = TareaAvance
        fields = ['horasReales', 'fechaAvance'] + [f'dia_{i}' for i in range(1, 32)]
        labels = {
            'horasReales': 'Horas reales',
        }
        widgets = {
            'horasReales': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese horas reales'
                }
            ),
            'fechaAvance': forms.HiddenInput(),  # Widget oculto para fechaAvance
            # Generar widgets para cada día
            **{f'dia_{i}': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese horas dedicadas y restantes'}) for i in range(1, 32)}
        }



class SprintHistoriasUsuarioForm(forms.ModelForm):
    Historias = forms.ModelMultipleChoiceField(
        queryset=HistoriaUsuario.objects.none(),  # Inicialmente vacío
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    def __init__(self, *args, **kwargs):
        pk_proyecto = kwargs.pop('pk', None)  # Extraer el pk del proyecto
        super(SprintHistoriasUsuarioForm, self).__init__(*args, **kwargs)
        if pk_proyecto:
            
            self.fields['Historias'].queryset = HistoriaUsuario.objects.filter(
                Sprint__isnull=True,
                Proyecto__pk=pk_proyecto
            )

    class Meta:
        model = HistoriaUsuario
        fields = ['Historias']

# Checkbox

class SprintBacklogForm(forms.Form):
    
    Empleado = forms.ModelChoiceField(widget=forms.Select(
                attrs = {
                    'class':'form-control',
                }
            ), required=True, queryset=None)

    def __init__(self,*args,**kwargs):
        Pk= kwargs.pop('pk')
        super().__init__(*args, **kwargs)
        self.fields['Empleado'].queryset = Empleado.objects.filter(DetalleEmpleado__Proyecto__pk=Pk)
    
        



class ReunionDiariaForm(forms.ModelForm):
    class Meta:
        model = ReunionDiaria
        fields = ['fecha','observaciones',]
        labels = {
            'fecha':'Fecha de reunión',
            'observaciones':'Observaciones',
        }
        widgets={
            'fecha': DateInput(
                format="%Y-%m-%d",
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese fecha de reunión'
                }),
            'observaciones':  forms.Textarea(
                attrs = {
                    'class':'form-control',
                    'rows':'3',
                    'placeholder': 'Ingrese Observaciones'
                }
            ),
        }


class TareaEmpleadoForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['fechainicioreal','fechafinalreal']
        labels = {
            'fechainicioreal':'Fecha de inicio real',
            'fechafinalreal':'Fecha de terminación real',
        }
        widgets={
            
             'fechainicioreal': DateInput(
                format="%Y-%m-%d",
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese fecha de inicio real'
                }
            ),
         
             'fechafinalreal': DateInput(
                format="%Y-%m-%d",
                attrs = {
                    'class':'form-control',
                    'placeholder':'Ingrese fecha de terminación real'
                }
            ),
            
        }


class ProgresoEmpleadoForm(forms.ModelForm):
    class Meta:
        model = Progreso
        fields = ['horasinvertivas']
        labels = {
            'horasinvertivas':'Horas invertidas',
        }
        widgets={
            
              'horasinvertivas': forms.NumberInput(
                attrs = {
                    'class':'form-control',
                    'placeholder': 'Ingrese las horas invertidas'
                }
            ),
            
        }


class EmpleadoProyectoForm(forms.Form):
   
    EmpleadoProyecto = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple(
                attrs = {
                    'class':'form-control',
                }
            ), required=True, queryset=None)

    def __init__(self,*args,**kwargs):
        Pk= kwargs.pop('pk')
        super().__init__(*args, **kwargs)
        """ print("Ini.jmhb" , Empleado,  "Fin.jmhb" )
        print("Ini.jmhb" , Empleado.objects,  "Fin.jmhb" )
        print("Ini.jmhb" , Pk,  "Fin.jmhb" ) """
        self.fields['EmpleadoProyecto'].queryset =  Empleado.objects.exclude(DetalleEmpleado__Proyecto__pk=Pk)