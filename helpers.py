from django.http import HttpResponseRedirect


def login_required(function):
    def wrapper(request, *args, **kw):
        if not request.session.get("email"):
            return HttpResponseRedirect('/auth/')
        else:
            return function(request, *args, **kw)
    return wrapper


def authorized_only(function):
    def wrapper(request, *args, **kw):
        if not request.session.get("email"):
            return HttpResponseRedirect('/auth/')
        if not request.session.get("is_authorized"):
            return HttpResponseRedirect('/unauthorized/')
        return function(request, *args, **kw)
    return wrapper


def view_only_for_team2073(function):
    def wrapper(request, *args, **kw):
        if not request.session.get("email"):
            return HttpResponseRedirect('/auth/')
        
        # Block POST requests for team2073 members
        if request.method == 'POST' and not request.session.get("is_authorized"):
            return HttpResponseRedirect('/unauthorized/')
        
        comp_code = request.GET.get('comp', 'testing')
        email = request.session.get("email")
        
        # Allow authorized users everywhere, team2073 only in testing
        if request.session.get("is_authorized") or (comp_code == 'testing' and email.endswith('@team2073.com')):
            return function(request, *args, **kw)
        
        return HttpResponseRedirect('/unauthorized/')
    return wrapper