from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from authenticate.models import AuthorizedUser
from teams.models import Team_Match_Data
from django.db.models import Count

def admin_required(function):
    def wrapper(request, *args, **kw):
        email = request.session.get("email")
        if not email:
            return HttpResponseRedirect('/auth/')
        # Temporarily disabled - first user can add themselves
        # if not AuthorizedUser.objects.filter(email=email).exists():
        #     return HttpResponseRedirect('/auth/unauthorized/')
        return function(request, *args, **kw)
    return wrapper

@admin_required
def admin_panel(request):
    comp_code = request.GET.get('comp', 'testing')
    
    # Get all authorized users
    users = AuthorizedUser.objects.all().order_by('email')
    
    # Get unique competitions from Team_Match_Data
    competitions = Team_Match_Data.objects.values_list('event', flat=True).distinct().order_by('event')
    
    # Get scout leaderboard for the competition
    leaderboard = Team_Match_Data.objects.filter(event=comp_code).values('scout_name').annotate(
        match_count=Count('id')
    ).order_by('-match_count')
    
    return render(request, 'authenticate/admin.html', {
        'users': users,
        'leaderboard': leaderboard,
        'comp_code': comp_code,
        'competitions': competitions
    })

@admin_required
def add_user(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            AuthorizedUser.objects.get_or_create(email=email)
    return redirect('/admin-panel/')

@admin_required
def remove_user(request, user_id):
    AuthorizedUser.objects.filter(id=user_id).delete()
    return redirect('/admin-panel/')
