from django.shortcuts import render

from django.shortcuts import render
from django.http import HttpResponse

def insurance_quote_step(request):
    # Récupération des étapes dynamiques Wagtail
    steps = [
        {"id": 1, "name": "Informations du véhicule"},
        {"id": 2, "name": "Conducteur principal"},
        {"id": 3, "name": "Formules & Garanties"}
    ]
    
    total_steps = len(steps) + 1  # Nombre total d'étapes + 1 pour la landing page finale
    
    # Récupération de l'étape courante
    current_step = int(request.POST.get('current_step', 1))
    action = request.POST.get('action', 'next')

    # Gestion de la navigation
    if action == 'prev' and current_step > 1:
        current_step -= 1
    elif action == 'next':
        # Sauvegarder les données de l'étape dans la session
        session_data = request.session.get('quote_form_data', {})
        session_data.update(request.POST.dict())
        request.session['quote_form_data'] = session_data

        if current_step < total_steps:
            current_step += 1

    is_summary_step = (current_step == total_steps)
    summary_data = {}

    # Préparation du récapitulatif backend si on est sur la landing page finale
    if is_summary_step:
        raw_data = request.session.get('quote_form_data', {})
        # Filtrer et formater les clés/valeurs pour le rendu HTMX
        summary_data = {
            k.replace('_', ' ').title(): v 
            for k, v in raw_data.items() 
            if k not in ['csrfmiddlewaretoken', 'current_step', 'action'] and v
        }

    context = {
        'steps': steps,
        'active_step': steps[current_step - 1] if current_step <= len(steps) else None,
        'current_step': current_step,
        'total_steps': total_steps,
        'is_summary_step': is_summary_step,
        'summary_data': summary_data,
    }

    # Si c'est une requête HTMX, renvoyer uniquement le bloc partiel
    if request.headers.get('HX-Request'):
        return render(request, 'partials/step_form.html', context)

    return render(request, 'quote_page.html', context)