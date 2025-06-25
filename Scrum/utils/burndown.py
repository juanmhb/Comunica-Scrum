# Scrum/utils/burndown.py

from django.shortcuts import render, get_object_or_404
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import pyplot as plt
import io
from django.db.models import Sum, F, Value, OuterRef, Subquery
from django.db.models.functions import Coalesce
from Scrum.models import Sprint, Tarea, TareaAvance, Empleado
from datetime import timedelta

def generar_burndown_chart(fechas, reales, total_estimadas, titulo, nombre_dev=None):
    ideal = [total_estimadas - (total_estimadas / (len(fechas) - 1)) * i for i in range(len(fechas))]
    plt.figure(figsize=(10, 5))
    plt.plot(fechas, ideal, label='Ideal', linestyle='--', marker='o')
    plt.plot(fechas, reales, label='Real', linestyle='-', marker='x')

    for x, y in zip(fechas, ideal):
        plt.annotate(f"{int(round(y))}", (x, y), textcoords="offset points", xytext=(0, 8), ha='center', fontsize=8, color='green')
    for x, y in zip(fechas, reales):
        plt.annotate(f"{int(round(y))}", (x, y), textcoords="offset points", xytext=(0, -12), ha='center', fontsize=8, color='blue')

    plt.grid(True)
    plt.xticks(rotation=45)
    plt.xlabel('Fecha')
    plt.ylabel('Horas restantes')
    plt.title(f"{titulo}" + (f" - {nombre_dev}" if nombre_dev else ""))
    plt.legend()
    plt.tight_layout()
    return plt

# Scrum/utils/burndown_pdf.py (o donde organices lógica compartida)
def construir_pdf_burndown(sprint_id) -> tuple[io.BytesIO, Sprint]:
    sprint = get_object_or_404(Sprint, pk=sprint_id)
    tareas_sprint = Tarea.objects.filter(HistoriaUsuario__Sprint=sprint)

    avances_subquery = TareaAvance.objects.filter(
        tarea=OuterRef('pk'),
        horasDedicadas=0
    ).annotate(
        total=Coalesce(F('horasReales'), Value(0)) + Coalesce(F('horasRestantesCaptura'), Value(0))
    ).values('tarea').annotate(
        suma=Sum('total')
    ).values('suma')[:1]

    tareas_sprint = tareas_sprint.annotate(
        esfuerzo_total=Coalesce(Subquery(avances_subquery), F('horasestimadas'))
    )

    horas_estimadas = tareas_sprint.aggregate(total=Coalesce(Sum('horasestimadas'), Value(0)))['total']
    horas_reestimadas = tareas_sprint.aggregate(total=Coalesce(Sum('esfuerzo_total'), Value(0)))['total']

    inicio = sprint.fechainiciosprint
    fin = sprint.fechafinalsprint
    dias = (fin - inicio).days + 1
    fechas = [inicio + timedelta(days=i) for i in range(dias)]

    esfuerzo_por_dia = {fecha: 0 for fecha in fechas}
    avances = TareaAvance.objects.filter(tarea__in=tareas_sprint, horasDedicadas__gt=0).order_by('fechaAvance')
    for a in avances:
        if a.fechaAvance in esfuerzo_por_dia:
            esfuerzo_por_dia[a.fechaAvance] += a.horasDedicadas
    acumulado = 0
    reales = []
    for fecha in fechas:
        acumulado += esfuerzo_por_dia[fecha]
        reales.append(max(horas_estimadas - acumulado, 0))

    buffer = io.BytesIO()
    with PdfPages(buffer) as pdf:
        plt1 = generar_burndown_chart(fechas, reales, horas_estimadas, f'Gráfica Burndown Horas Estimadas Inicio - {sprint.nombresprint} ({inicio} al {fin})')
        pdf.savefig()
        plt1.close()

        if horas_estimadas != horas_reestimadas:
            acumulado = 0
            reales_reestimadas = []
            for fecha in fechas:
                acumulado += esfuerzo_por_dia[fecha]
                reales_reestimadas.append(max(horas_reestimadas - acumulado, 0))
            plt2 = generar_burndown_chart(fechas, reales_reestimadas, horas_reestimadas, f'Gráfica Burndown Horas Reestimadas - {sprint.nombresprint} ({inicio} al {fin})')
            pdf.savefig()
            plt2.close()

        developers = Empleado.objects.filter(
            Roles__NombreRol='Developers',
            DetalleEmpleado__Proyecto=sprint.Proyecto,
            #DetalleEmpleado__Status='1'
        ).distinct()
        #print(f"developers: {developers}")
        for dev in developers:
            # print(f"HistoriaUsuario__Sprint: {sprint}, Empleado: {dev} ")
            tareas_dev = Tarea.objects.filter(HistoriaUsuario__Sprint=sprint, Empleado=dev)
            # print(f"Desarrollador: {dev}, tareas encontradas: {tareas_dev.count()}")

            tareas_dev = Tarea.objects.filter(HistoriaUsuario__Sprint=sprint, Empleado=dev).annotate(
                esfuerzo_total=Coalesce(Subquery(avances_subquery), F('horasestimadas'))
            )
            # print(f"tareas_dev: {tareas_dev}")
            if not tareas_dev.exists():
                continue

            est = tareas_dev.aggregate(total=Coalesce(Sum('horasestimadas'), Value(0)))['total']
            reest = tareas_dev.aggregate(total=Coalesce(Sum('esfuerzo_total'), Value(0)))['total']

            esfuerzo_por_dia_dev = {f: 0 for f in fechas}
            avances_dev = TareaAvance.objects.filter(tarea__in=tareas_dev, horasDedicadas__gt=0).order_by('fechaAvance')
            for a in avances_dev:
                if a.fechaAvance in esfuerzo_por_dia_dev:
                    esfuerzo_por_dia_dev[a.fechaAvance] += a.horasDedicadas
            acumulado = 0
            reales_dev = []
            for f in fechas:
                acumulado += esfuerzo_por_dia_dev[f]
                reales_dev.append(max(est - acumulado, 0))
            plt3 = generar_burndown_chart(fechas, reales_dev, est, f'{dev.Usuario.get_full_name()}  Horas Estimadas - {sprint.nombresprint} ({inicio} al {fin})')
            pdf.savefig()
            plt3.close()

            if est != reest:
                acumulado = 0
                reales_reest_dev = []
                for f in fechas:
                    acumulado += esfuerzo_por_dia_dev[f]
                    reales_reest_dev.append(max(reest - acumulado, 0))
                plt4 = generar_burndown_chart(fechas, reales_reest_dev, reest, f'{dev.Usuario.get_full_name()} Horas Reestimadas - {sprint.nombresprint} ({inicio} al {fin})')
                                              

                pdf.savefig()
                plt4.close()

    buffer.seek(0)
    return buffer, sprint
