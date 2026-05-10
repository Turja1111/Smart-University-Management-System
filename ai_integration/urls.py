from django.urls import path
from . import views

urlpatterns = [
    path('chatbot/', views.chatbot_query, name='chatbot'),
    path('weak-students/', views.weak_student_prediction, name='weak_students'),
    path('assignment-summary/<int:submission_id>/', views.assignment_summary, name='assignment_summary'),
    path('plagiarism-check/<int:submission_id>/', views.plagiarism_check, name='plagiarism_check'),
    path('reputation-score/', views.reputation_score, name='reputation_score'),
    path('reputation-score/<int:student_id>/', views.reputation_score, name='reputation_score_by_id'),
]
