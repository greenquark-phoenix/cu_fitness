from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import FitnessEvent, EventParticipation
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.timezone import now


def event_list(request):
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', 'date')

    if query:
        events = FitnessEvent.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        )
    else:
        events = FitnessEvent.objects.all()

    if sort_by == 'popularity':
        events = events.order_by('-popularity')
    else:
        events = events.order_by('event_date')

    return render(request, 'events/event_list.html', {'events': events})


def event_detail(request, event_id):
    event = get_object_or_404(FitnessEvent, id=event_id)
    joined = False
    if request.user.is_authenticated:
        joined = EventParticipation.objects.filter(event=event, user=request.user).exists()
    return render(request, 'events/event_detail.html', {'event': event, 'joined': joined})


@login_required
def join_event(request, event_id):
    event = get_object_or_404(FitnessEvent, id=event_id)
    EventParticipation.objects.get_or_create(event=event, user=request.user)
    return redirect('events:event_detail', event_id=event_id)


@login_required
def my_events(request):
    participations = EventParticipation.objects.filter(user=request.user)
    return render(request, 'events/my_events.html', {'participations': participations})

def calendar_view(request):
    return render(request, 'events/calendar.html')

def event_json(request):
    events = FitnessEvent.objects.all()
    data = []

    for event in events:
        data.append({
            'title': event.title,
            'start': event.event_date.isoformat(),
            'url': f"/events/{event.id}/"
        })

    return JsonResponse(data, safe=False)
