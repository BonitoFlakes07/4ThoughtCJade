from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # moderation routes — must come before the slug catch-all below
    path('mod/login/', views.mod_login, name='mod_login'),
    path('mod/logout/', views.mod_logout, name='mod_logout'),
    path('mod/', views.mod_dashboard, name='mod_dashboard'),
    path('mod/thread/<int:thread_id>/pin/', views.mod_toggle_pin, name='mod_toggle_pin'),
    path('mod/thread/<int:thread_id>/lock/', views.mod_toggle_lock, name='mod_toggle_lock'),
    path('mod/thread/<int:thread_id>/delete/', views.mod_delete_thread, name='mod_delete_thread'),
    path('mod/reply/<int:reply_id>/delete/', views.mod_delete_reply, name='mod_delete_reply'),
    path('mod/board/<int:board_id>/delete/', views.mod_delete_board, name='mod_delete_board'),
    path('mod/report/<int:report_id>/resolve/', views.mod_resolve_report, name='mod_resolve_report'),

    # public board/thread routes
    path('<slug:slug>/', views.board_detail, name='board_detail'),
    path('<slug:slug>/thread/<int:thread_id>/', views.thread_detail, name='thread_detail'),
    path('<slug:slug>/thread/<int:thread_id>/report/', views.report_thread, name='report_thread'),
    path('<slug:slug>/thread/<int:thread_id>/reply/<int:reply_id>/report/', views.report_reply, name='report_reply'),
]