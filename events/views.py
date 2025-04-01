from django.shortcuts import render, get_object_or_404, redirect
from .models import FitnessEvent, EventParticipation
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.timezone import now


def event_list(request):
    query = request.GET.get('q', '')  # Get the search keyword from the user
    sort_by = request.GET.get('sort', 'date')  # Get the sorting method, default is by date

    if query:
        # If there is a search keyword, filter events by title, description, and location
        events = FitnessEvent.objects.filter(
            Q(title__icontains=query) |  # Fuzzy search for event title
            Q(description__icontains=query) |  # Fuzzy search for event description
            Q(location__icontains=query)  # Fuzzy search for event location
        )
    else:
        # If no search keyword, return all events
        events = FitnessEvent.objects.all()

    if sort_by == 'popularity':
        events = events.order_by('-popularity')  # Assuming you have a "popularity" field
    else:
        events = events.order_by('event_date')  # Default to sorting by event date

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
