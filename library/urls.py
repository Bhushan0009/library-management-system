from django.contrib import admin
from django.urls import path, include
from library_app import views
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    path('', views.home, name='home'),

    path('adminsignup/', views.adminsignup_view, name='adminsignup'),
    path('studentsignup/', views.studentsignup_view, name='studentsignup'),

    path('adminlogin/', views.admin_login_view, name='adminlogin'),
    path('studentlogin/', views.student_login_view, name='studentlogin'),

    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

    path('afterlogin/', views.afterlogin_view, name='afterlogin'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),

    path('addbook/', views.addbook_view, name='addbook'),
    path('viewbook/', views.viewbook_view, name='viewbook'),
    path('issuebook/', views.issuebook_view, name='issuebook'),
    path('viewissuedbook/', views.viewissuedbook_view, name='viewissuedbook'),
    path('viewstudent/', views.viewstudent_view, name='viewstudent'),
    path('viewissuedbookbystudent/', views.viewissuedbookbystudent, name='viewissuedbookbystudent'),
    path('return_book/<int:book_id>/', views.return_book_view, name='return_book'),
    path('deletebook/<int:book_id>/', views.delete_book_view, name='delete_book'),
    path('editbook/<int:book_id>/', views.edit_book_view, name='edit_book'),
    path('deletestudent/<int:student_id>/', views.delete_student_view, name='deletestudent'),
    path('reports/', views.reports_view, name='reports'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)