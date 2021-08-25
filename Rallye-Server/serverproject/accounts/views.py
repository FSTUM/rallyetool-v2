from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth


def login(request):
	if request.method == 'POST':
		user = auth.authenticate(username=request.POST['username'], password=request.POST['password'])
		if user is not None:
			auth.login(request, user)
			return redirect('rate')
			#return render(request, 'ratings/rate.html', {'login': False})
		else:
			return render(request, 'accounts/login.html', {'error': 'Invalid username or password.', 'login': True})
	else:
		return render(request, 'accounts/login.html', {'login': True})

def logout(request):
	if request.method == 'POST':
		auth.logout(request)
		return render(request, 'accounts/login.html', {'login': True})
	return render(request, 'acounts/login.html', {'login': True})