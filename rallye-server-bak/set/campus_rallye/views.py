from django.shortcuts import render
from django.db.models import Sum
from django.http import HttpResponseRedirect

from .models import Laufgruppe, Stand, Bewertung

"""
def CurrentIndex(request, stand_token):
    current_stand = Stand.objects.get(token=stand_token)
    # Hier muss noch nachgebessert werden. Die bereits Bewerteten Gruppen sollen nicht mehr angezeigt werden.
    gruppen = Laufgruppe.objects.all()
    punkte = {x for x in range(11)}
    context = {'stand': current_stand, 'gruppen': gruppen, 'punkte': punkte}
    if request.method == 'POST':
        gruppen_id = request.POST.get('gruppen')
        bewertungs_punkte = request.POST.get('punkte')
        # Nachschauen ob bereits Element existiert
        results = Bewertung.objects.filter(lg_id=gruppen_id, st_token=stand_token).exists()
        if results:
            # Falls bereits eine Bewertung vorliegt wird ein Fehler auf der Seite angezeigt und die Bewertung nicht gespeichert.
            context['error_message'] = "Diese Gruppe wurde von dir bereits bewertet."
            return render(request, 'campus_rallye/index.html', context)
        else:
            if Laufgruppe.objects.filter(laufgruppen_id=gruppen_id).exists():
                print("I get insiode")
                laufgr = Laufgruppe.objects.get(laufgruppen_id=gruppen_id)
                stand = Stand.objects.get(token=stand_token)
                b = Bewertung(lg_id=laufgr, st_token=stand, punkte=bewertungs_punkte)
                b.save()
            else:
                context['error_message'] = "Diese Gruppe existiert nicht."
    return render(request, 'campus_rallye/index.html', context)
"""


def index(request, stand_token):
    current_stand = Stand.objects.get(token=stand_token)
    gruppen_einer = {x for x in range(1,11)}
    punkte = {x for x in range(11)}
    gruppen_zehner = gruppen_hunderter = {x for x in range(10)}
    context = {'stand': current_stand, 'hunderter': gruppen_hunderter, 'zehner': gruppen_zehner, 'einer':  gruppen_einer, 'punkte': punkte}
    if request.method == 'POST':
        bewertungs_punkte = request.POST.get('punkte')
        gruppe_hunderter = request.POST.get('hunderter')
        gruppe_zehner = request.POST.get('zehner')
        gruppe_einer = request.POST.get('einer')
        gruppen_id = gruppe_hunderter + gruppe_zehner + gruppe_einer
        results = Bewertung.objects.filter(lg_id=gruppen_id, st_token=stand_token).exists()
        if results:
            # Falls bereits eine Bewertung vorliegt wird ein Fehler auf der Seite angezeigt und die Bewertung nicht gespeichert.
            context['error_message'] = "Diese Gruppe wurde von dir bereits bewertet."
            return render(request, 'campus_rallye/index.html', context)
        else:
            if Laufgruppe.objects.filter(laufgruppen_id=gruppen_id).exists():
                laufgr = Laufgruppe.objects.get(laufgruppen_id=gruppen_id)
                stand = Stand.objects.get(token=stand_token)
                b = Bewertung(lg_id=laufgr, st_token=stand, punkte=bewertungs_punkte)
                b.save()
            else:
                context['error_message'] = "Diese Gruppe existiert nicht."
    return render(request, 'campus_rallye/index.html', context)


def bewertung(request):
    laufgruppen = Laufgruppe.objects.all()
    for laufgruppe in laufgruppen:
        if Bewertung.objects.filter(lg_id=laufgruppe.laufgruppen_id).exists():
            zuBerechnen = Bewertung.objects.filter(lg_id=laufgruppe.laufgruppen_id).aggregate(Sum('punkte'))
            print(zuBerechnen)
            laufgruppe.total_punkte = zuBerechnen['punkte__sum']
            laufgruppe.save()
    context = {'gruppen': Laufgruppe.objects.order_by('total_punkte').reverse(),
                }

    if Laufgruppe.objects.filter(bester_name=True).count() > 0:
        context['bester_name'] = Laufgruppe.objects.get(bester_name=True)
    return render(request, 'campus_rallye/bewertung.html', context)
