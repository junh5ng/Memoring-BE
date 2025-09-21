from django.urls import path

from .views import MissionCandidatesView, MissionSelectView, MissionCurrentView, MissionScheduleView, MissionVoiceView, MissionCompleteView, MissionGiveupView


urlpatterns = [
    path('candidates/', MissionCandidatesView.as_view()),
    path('select/', MissionSelectView.as_view()),
    path('current/', MissionCurrentView.as_view()),
    path('<int:mission_id>/schedule/', MissionScheduleView.as_view()),
    path('<int:mission_id>/voice/', MissionVoiceView.as_view()),      # GET/POST 분리해도 되나 여기선 하나의 View에서 메서드 분기
    path('<int:mission_id>/complete/', MissionCompleteView.as_view()),
    path('<int:mission_id>/giveup/', MissionGiveupView.as_view()),
]