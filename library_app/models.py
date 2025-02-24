from django.db import models
from datetime import date, timedelta
from django.contrib.auth.models import User

# Book model
class Book(models.Model):
    genres= [
        ('education', 'Education'),
        ('entertainment', 'Entertainment'),
        ('comics', 'Comics'),
        ('biography', 'Biography'),
        ('history', 'History'),
        ('novel', 'Novel'),
        ('fantasy', 'Fantasy'),
        ('thriller', 'Thriller'),
        ('romance', 'Romance'),
        ('scifi','Sci-Fi')
        ]
    title=models.CharField(max_length=200,unique=True)
    author = models.CharField(max_length=200)
    genre=models.CharField(max_length=30,choices=genres,default='education')
    publication_year = models.PositiveIntegerField()
    isbn=models.IntegerField(unique=True)
    total_copies = models.IntegerField()
    available_copies = models.IntegerField()

    def __str__(self):
        return f"{self.title} by {self.author} (Available: {self.available_copies} / Total: {self.total_copies})"

# Student model 
class Student(models.Model):
    Branches = [
        ('CS', 'Computer Science'),
        ('CIVIL', 'Civil Engineering'),
        ('MECH', 'Mechanical Engineering'),
    ]
    
    user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    enrollment = models.IntegerField()
    branch = models.CharField(max_length=40,choices=Branches)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

# Issued Book model
class IssuedBook(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    issuedate = models.DateField(auto_now_add=True)
    expirydate = models.DateField(default=date.today() + timedelta(days=15))
    
    def __str__(self):
        return f"{self.book.title} issued to {self.student.user.get_full_name()}"