from django.http import HttpResponse

def testchat_view(request):
    return HttpResponse(request, "Boo!!!")