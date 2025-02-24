from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout, login, authenticate
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.contrib import messages
from datetime import date


# home view
def home(request):
    if request.user.is_authenticated:
        return redirect('afterlogin')
    return render(request,'index.html')


# login and signup views
def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()
def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')
def student_dashboard(request):
    return render(request, 'student_dashboard.html')

@login_required
def afterlogin_view(request):
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('admin_dashboard')
        elif is_student(request.user):
            return redirect('student_dashboard')
    return redirect('home')

def admin_login_view(request):
    form = AuthenticationForm()
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if is_admin(user):
                login(request, user)
                messages.success(request, "Login successful. Welcome Admin!")
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Access Denied: You are not an admin.")
                return redirect('adminlogin')
        else:
            messages.error(request, "Invalid credentials. Please try again.")

    return render(request, "adminlogin.html", {'form': form})

def student_login_view(request):
    form = AuthenticationForm()
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            if is_student(user):  
                login(request, user)
                messages.success(request, "Login successful. Welcome Student!")
                return redirect('student_dashboard')
            else:
                messages.error(request, "Access Denied: You are not a student.")
                return redirect('studentlogin')
        else:
            messages.error(request, "Invalid credentials. Please try again.")

    return render(request, "studentlogin.html", {'form': form})

def adminsignup_view(request):
    form=AdminSignupForm()
    if request.method=='POST':
        form=AdminSignupForm(request.POST)
        if form.is_valid():
            user=form.save()
            
            my_admin_group = Group.objects.get_or_create(name='ADMIN')
            my_admin_group[0].user_set.add(user)
            messages.success(request, "Admin account created successfully! Please log in.")

            return redirect(reverse('adminlogin'))
    return render(request,'adminsignup.html',{'form':form})

def studentsignup_view(request):
    form=StudentSignupForm()
    if request.method=='POST':
        form=StudentSignupForm(request.POST)
        if form.is_valid():
            user=form.save()

            Student.objects.create(
                user=user,
                enrollment=form.cleaned_data['enrollment'],
                branch=form.cleaned_data['branch']
            )

            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
            messages.success(request, "Admin account created successfully! Please log in.")

        return redirect(reverse('studentlogin'))
    return render(request,'studentsignup.html', {'form':form})

def logout_view(request):
    logout(request)
    messages.success(request,'Logged Out Successfully!')
    return redirect('home')


# Books View
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def addbook_view(request):
    form = BookForm()

    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save(commit=False)  # Don't save yet
            book.available_copies = book.total_copies  # Set available = total copies
            book.save()  # Now save to database
            return redirect('viewbook')  # Redirect to book list after adding

    return render(request, 'addbook.html', {'form': form, "title": "Add New Book"})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def edit_book_view(request, book_id):
    book = Book.objects.get(id=book_id)

    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            book = form.save(commit=False)
            book.available_copies = book.total_copies
            book.save()
            return redirect("viewbook")
    else:
        form = BookForm(instance=book)
    return render(request, "addbook.html", {"form": form, "title": "Edit Book Details"})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewbook_view(request):
    books=Book.objects.all()
    return render(request,'viewbook.html',{'books':books})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def issuebook_view(request):
    form = IssuedBookForm()

    if request.method == 'POST':
        form = IssuedBookForm(request.POST)
        if form.is_valid():
            book = form.cleaned_data['book']
            student = form.cleaned_data['student']

            # Check if book is available
            if book.available_copies <= 0:
                messages.error(request, f"{book.title} is not available for issue.")
                return redirect('issuebook')

            # Issue book
            issued_book = IssuedBook(
                student=student,
                book=book,
                issuedate=date.today(),
                expirydate=date.today() + timedelta(days=15)  # 15 days from issue date
            )
            issued_book.save()

            # Update book count
            book.available_copies -= 1
            book.save()

            messages.success(request, f"Book '{book.title}' issued to {student.user.get_full_name()} successfully!")
            return redirect('viewissuedbook')

    return render(request, 'issuebook.html', {'form': form})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewissuedbook_view(request):
    issuedbooks = IssuedBook.objects.select_related('book', 'student__user').all()

    if not issuedbooks.exists():
        messages.info(request, "No books have been issued yet.")

    # Attach fine calculation directly to each issued book object
    for ib in issuedbooks:
        days = (date.today() - ib.issuedate).days
        ib.fine = max(0, (days - 15) * 10) if days > 0 else 0  # Fine applies after 15 days

    return render(request, 'viewissuedbook.html', {'issuedbooks': issuedbooks})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def return_book_view(request, book_id):
    try:
        issued_book = IssuedBook.objects.filter(book_id=book_id).first()  # Get only one issued copy

        if issued_book:
            book = issued_book.book
            book.available_copies += 1  # Increase available copies
            book.save()
            issued_book.delete()  # Remove only one issued record

            messages.success(request, "Book returned successfully.")
        else:
            messages.error(request, "No issued book found for return.")

    except Exception as e:
        messages.error(request, f"An error occurred: {e}")

    return redirect('viewissuedbook')

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_book_view(request, book_id):
    try:
        book = Book.objects.get(id=book_id)

        # Ensure the book is not currently issued
        if IssuedBook.objects.filter(book_id=book_id).exists():
            messages.error(request, "Cannot delete book. It is currently issued.")
        else:
            book.delete()
            messages.success(request, f'Book "{book.title}" deleted successfully!')

    except Book.DoesNotExist:
        messages.error(request, "Book not found.")

    return redirect('viewbook')  # Redirect to books list page


from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from datetime import date
from .models import IssuedBook
from django.utils.timezone import now

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reports_view(request):
    # Overdue Books Report
    overdue_books = IssuedBook.objects.filter(expirydate__lt=now())
    
    for book in overdue_books:
        days_overdue = (now().date() - book.expirydate).days
        book.fine = days_overdue * 5  # Assuming fine is $5 per day
    
    # Top Students Report
    month = request.GET.get('month', now().month)  # Default to current month
    top_students = (
    Student.objects.annotate(
        total_books=Count(
            'issuedbook', 
            filter=Q(issuedbook__issuedate__month=month)  # Use issuedate instead of issue_date
        )
    )
    .order_by('-total_books')[:10]
)
    
    context = {
        'overdue_books': overdue_books,
        'top_students': top_students,
    }
    return render(request, 'reports.html', context)


# Student View
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def viewstudent_view(request):
    students=Student.objects.select_related('user').all()
    return render(request,'viewstudent.html',{'students':students})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_student_view(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
        user = student.user  # Get the associated user account

        # Delete student and user account
        student.delete()
        user.delete()

        messages.success(request, "Student deleted successfully.")
    except Student.DoesNotExist:
        messages.error(request, "Student not found.")

    return redirect('viewstudent')  # Redirect to student list page

@login_required(login_url='studentlogin')
def viewissuedbookbystudent(request):
    # Get the logged-in student record
    student = Student.objects.filter(user=request.user).first()

    if not student:
        return render(request, 'viewissuedbookbystudent.html', {'error': 'Student record not found'})

    # Fetch issued books for the student
    issued_books = IssuedBook.objects.filter(student=student).select_related('book')

    issued_details = []
    
    for issued in issued_books:
        book = issued.book  
        issue_date = issued.issuedate.strftime("%d-%m-%Y")
        expiry_date = issued.expirydate.strftime("%d-%m-%Y")

        # Calculate fine manually
        overdue_days = max(0, (date.today() - issued.expirydate).days)
        fine = overdue_days * 10 if overdue_days > 0 else 0

        issued_details.append({
            'book': book.title,
            'author': book.author,
            'issuedate': issue_date,
            'expirydate': expiry_date,
            'fine': fine,
        })

    return render(request, 'viewissuedbookbystudent.html', {'issued_books': issued_details, 'student': student})