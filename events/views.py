from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import FitnessEvent, EventParticipation
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
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

    paginator = Paginator(events, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'events/event_list.html', {
        'events': page_obj,
        'page_obj': page_obj,
        'request': request
    })


def event_detail(request, event_id):
    event = get_object_or_404(FitnessEvent, id=event_id)
    joined = False
    favorited = False

    if request.user.is_authenticated:
        joined = EventParticipation.objects.filter(event=event, user=request.user).exists()
        favorited = event.favorited_by.filter(id=request.user.id).exists()

    return render(request, 'events/event_detail.html', {
        'event': event,
        'joined': joined,
        'favorited': favorited
    })


@login_required
def join_event(request, event_id):
    event = get_object_or_404(FitnessEvent, id=event_id)
    EventParticipation.objects.get_or_create(event=event, user=request.user)
    return redirect('events:event_detail', event_id=event_id)


@login_required
def my_events(request):
    participations = EventParticipation.objects.filter(user=request.user)
    return render(request, 'events/my_events.html', {'participations': participations})


@login_required
def toggle_favorite(request, event_id):
    event = get_object_or_404(FitnessEvent, id=event_id)

    if request.user in event.favorited_by.all():
        event.favorited_by.remove(request.user)
    else:
        event.favorited_by.add(request.user)

    return redirect('events:event_detail', event_id=event_id)


@login_required
def my_favorites(request):
    events = request.user.favorite_events.all()
    return render(request, 'events/my_favorites.html', {'events': events})


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
