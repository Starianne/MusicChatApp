from django.shortcuts import redirect

def not_logged_in_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('account/spotifylogin')
        #   then check if user is logged into spotify using something but idk yet?
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func