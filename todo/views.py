from django.shortcuts import render, redirect, get_object_or_404
# Import django 'UserCreationForm'
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# We import the User object from the following library
from django.contrib.auth.models import User
from django.db import IntegrityError
# We import now the login method 
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request):
    return render(request, 'todo/home.html')


def signupuser(request):
    """
    NOTE: every time someone write something on a URL and then
    press <ENTER>, this is coming to the web server as a 'GET'
    request. A 'POST' request can only come through a <form>.
    We can use this to guide the action of this function.
    """
    # We now pass the UserCreationForm object as a dictionary to 
    # the template
    if request.method == 'GET':
        # if the method is 'GET', we then create a new user
        return render(request, 'todo/signupuser.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], \
                        password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                return render(request, 'todo/signupuser.html', {
                            'form': UserCreationForm(),
                            'error':'That username has already been taken. Please choose a new one'})
        else:
            # Tell the user the passwords didn't match
            return render(request, 'todo/signupuser.html', {
                            'form': UserCreationForm(),
                            'error':'Passwords did not match'})


def loginuser(request):
    """
    SE-NOTE This method is very similar to the signup one. So we can start by copying
    the code from that method here.
    Then we modify the render request so to return loginuser.html, instead of 
    signupuser.html. And we are using a different form, provided by Django,
    the AuthenticationForm, to remplace the UserCreationForm.
    Of course the AuthenticationForm has to be imported.
    """
    if request.method == 'GET':
        # if the method is 'GET', we then go to the loginuser form
        return render(request, 'todo/loginuser.html', {'form': AuthenticationForm()})
    else:
        # SE-NOTE: This means we are calling this method as a consequence of 
        # filling in the authentication form, which comes, by design as a POST 
        # request.
        # To check username and password, we need to import the module 'authenticate'
        # authenticate returns an user object. If the user does not exist it returns
        # None
        user = authenticate(request, username=request.POST['username'], \
                                    password=request.POST['password'])
        if user is None:
            return render(request, 'todo/loginuser.html', {
                            'form': AuthenticationForm(),
                            'error': 'Incorrect username or password'})
        else:
            # The user has been found, so use the same lines as after the creation of 
            # a new user
            login(request, user)
            return redirect('currenttodos')

# '@login_required' tells Django that only users who have looged in can run the next
# function
@login_required
def logoutuser(request):
    # SE-NOTE: it is really important to check if this is coming as a 'POST'
    # request. If 'logoutuser' comes as a 'GET' request, browsers like Chrome
    # would preload all the <a> tags in the page in the background to speed up
    # experience with the net result of logging out users immediately...
    # This is definitely difficult to troubleshoot...
    # Checking for a 'POST' request allwos ignoring any 'GET' request coming
    # from the browser.
    # To do a logout, we need to import the 'logout' method (see import section
    # above)
    if request.method == 'POST':
        logout(request)
        return redirect('home')



@login_required
def createtodo(request):
    if request.method == 'GET':
        # if the method is 'GET', we then go to the loginuser form
        return render(request, 'todo/createtodo.html', {'form': TodoForm()})
    else:
        try:
            # We react to the 'POST' request and we assign TodoForm, as we specified it
            # to the form instance
            form = TodoForm(request.POST)
            # We then create a new variable, called newtodo, where we temporarly store
            # the form. NOTE 'commit=False', which means we do not store the form to 
            # the Db yet, as we have to assign the todo to a specific user.
            newtodo = form.save(commit=False)
            # We assign the same user making the request to the newtodo
            newtodo.user = request.user
            # And we can now save the todo to the Db
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html', {
                            'form': TodoForm(),
                            'error': 'Bad Input Data. Please try again.'})

@login_required
def currenttodos(request):
    """
    Import the Todos from the Db, using the Todo object (see import section)
    NOTE: todos = Todo.objects.all() gets all the todos for every user. We need
    to be more specific than this.
    """
    #todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    todos = Todo.objects.filter(user=request.user, completed=False)
    return render(request, 'todo/currenttodos.html', {'todos':todos})


@login_required
def completedtodos(request):
    """
    Import the Todos from the Db, using the Todo object (see import section)
    NOTE: todos = Todo.objects.all() gets all the todos for every user. We need
    to be more specific than this.
    """
    #todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    todos = Todo.objects.filter(user=request.user, completed=True).order_by('-datecompleted')
    return render(request, 'todo/completedtodos.html', {'todos':todos})


@login_required
def viewtodo(request, todo_pk):
    # We use the 'get_object_or_404' method we imported to retrieve from the model
    # 'Todo' the instance wiht 'pk' (primary key in Db terminology) equal to the
    # blog_id
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    if request.method == 'GET':
        # To visualize the todo and allows for modifications we can pass the todo via a
        # a form, 'TodoForm', which we have defined for 'createtodo'.
        # Instance allows the form to be loaded with a specific instance of the object.
        form = TodoForm(instance=todo)
        # We then pass it via render to the proper template
        return render(request, 'todo/viewtodo.html', {'todo': todo, 'form': form})
    else:
        try:
            # We get the form from the html page
            # SE_NOTE: we have to define the specific instance to avoid the error:
            #       'NOT NULL constraint failed: todo_todo.user_id'
            # To avoid this we have to identify the specific instance using passing
            # the parameter 'instance=todo'
            form = TodoForm(request.POST, instance=todo)
            # And simply def save(self, *args, **kwargs):
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/vietodo.html', {
                            'todo': todo,
                            'form': form,
                            'error': 'Bad info'})



@login_required
def completetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    # This has to be triggered by a 'POST' request ONLY!
    if request.method == 'POST':
        # To mark the todo is complete we set the time in 'datecompleted'
        # Of course we need to import timezone
        todo.datecompleted = timezone.now()
        todo.completed = True
        todo.save()
        return redirect('currenttodos')

@login_required
def deletetodo(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    # This has to be triggered by a 'POST' request ONLY!
    if request.method == 'POST':
        # To mark the todo is complete we set the time in 'datecompleted'
        # Of course we need to import timezone
        todo.delete()
        return redirect('currenttodos')
        