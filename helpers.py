from django.http import HttpResponseRedirect


def login_required(function):
    def wrapper(request, *args, **kw):
        print(request.session.get("email"))
        if not request.session.get("email"):
            return HttpResponseRedirect('/auth/')
        else:
            return function(request, *args, **kw)

    return wrapper
