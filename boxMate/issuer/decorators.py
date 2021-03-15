from django.shortcuts import redirect

def is_issuer(function):
    """
    decorator to check if logged in user is issuer
    :param function:
    :return: redirect to create issuer if not issuer
    By: Amira
    Created at: 14/3/2021
    """
    def wrap(request, *args, **kwargs):
        user = request.user
        if user.issuer:
            return function(request, *args, **kwargs)
        else:
            return redirect('issuer:create-issuer')

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap