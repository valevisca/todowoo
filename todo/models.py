from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Todo(models.Model):
    title = models.CharField(max_length=100)
    memo = models.TextField(blank=True)
    datecreated = models.DateTimeField(auto_now_add=True)
    datedue = models.DateField(null=True, blank=True)
    datecompleted = models.DateField(null=True, blank=True)
    important = models.BooleanField(default=False)
    # We have to put here a reference to the user. To do this, we have to use 
    # a ForeignKey which allows us to conenct a model to another.
    # This is a "one to many relationship", as one user can have many 
    # Todos, but one todo belongs to one user ONLY.
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # The following instances come from other projects, but we are not using them...
    #todofile = models.ImageField(upload_to='todo/todofiles')

    # SE-Note: Setting 'blank=True' tells the field is optional. This can be used 
    # with the other fields as well. On dates/time we can also use 'null=True'.
    #url = models.URLField(blank=True)

    def __str__(self):
        return self.title