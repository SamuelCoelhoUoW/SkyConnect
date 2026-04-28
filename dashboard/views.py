# Author: Theoayman Haid De Azevedo
# Individual element - wrote the code

from django.shortcuts import render
from teams.views import team_list
from user_messages.models import user_messages

# Create your views here.
def dashboard_view(request):
    inbox = user_messages.objects.filter(
        receiver=request.user,
        is_draft=False
    ).order_by('-id')

    return render(request, 'dashboard.html', {
        'inbox': inbox,
    })

def dashboard_search(request):
    return team_list(request)