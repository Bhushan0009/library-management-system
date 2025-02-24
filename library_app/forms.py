from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Book,Student,IssuedBook
import datetime

class BookForm(forms.ModelForm):
    class Meta:
        model=Book
        fields=['title','author','genre','publication_year','isbn','total_copies']

class IssuedBookForm(forms.ModelForm):
    class Meta:
        model=IssuedBook
        fields = ['book', 'student']

class StudentSignupForm(UserCreationForm):
    branch = forms.ChoiceField(choices=Student.Branches)
    current_year = datetime.datetime.now().year
    enrollment = forms.ChoiceField(
        choices=[(year, year) for year in range(current_year - 20, current_year + 1)],
        label="Enrollment Year"
    )
    class Meta:
        model=User
        fields=['username', 'first_name', 'last_name', 'password1', 'password2']

class AdminSignupForm(UserCreationForm):
    class Meta:
        model=User
        fields=['username', 'first_name', 'last_name', 'password1', 'password2']