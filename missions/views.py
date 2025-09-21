from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers
from .models import Mission, UserMission
from .serializers import MissionSerializer, UserMissionCurrentSerializer


class MissionCandidatesView(APIView):
    def get(self, request):
        qs = Mission.objects.filter(is_active=True).order_by('id')[:3]
        return Response(MissionSerializer(qs, many=True).data)


class MissionSelectView(APIView):
    def post(self, request):
        mission_id = request.data.get('mission_id')
        try:
            m = Mission.objects.get(id=mission_id, is_active=True)
        except Mission.DoesNotExist:
            return Response({"detail":"미션을 찾을 수 없습니다."}, status=404)
        um = UserMission.objects.create(user=request.user, mission=m)
        return Response({"mission_id": um.id, "status": "SELECTED"}, status=201)


class MissionCurrentView(APIView):
    def get(self, request):
        um = UserMission.objects.filter(user=request.user, given_up=False).order_by('-created_at').first()
        if not um:
            return Response({"has_mission": False})
        data = UserMissionCurrentSerializer(um).data
        return Response({"has_mission": True, "mission": data})


class MissionScheduleView(APIView):
    def patch(self, request, mission_id):
        try:
            um = UserMission.objects.get(id=mission_id, user=request.user)
        except UserMission.DoesNotExist:
            return Response(status=404)
        um.scheduled_at = request.data.get('scheduled_at', um.scheduled_at)
        aom = request.data.get('alarm_offset_minutes', um.alarm_offset_minutes)
        try:
            aom_int = int(aom)
            if 0 <= aom_int <= 720:
                um.alarm_offset_minutes = aom_int
        except (TypeError, ValueError):
            pass
        um.save()
        return Response({
            "mission_id": um.id,
            "scheduled_at": um.scheduled_at,
            "alarm_offset_minutes": um.alarm_offset_minutes
        })


class MissionVoiceView(APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, mission_id):
        try:
            um = UserMission.objects.get(id=mission_id, user=request.user)
        except UserMission.DoesNotExist:
            return Response(status=404)
        file = request.FILES.get('file')
        if not file:
            return Response({"detail":"file 필요"}, status=400)
        um.voice = file
        um.save()
        return Response({"mission_id": um.id, "voice_url": um.voice.url}, status=201)

    def get(self, request, mission_id):
        try:
            um = UserMission.objects.get(id=mission_id, user=request.user)
        except UserMission.DoesNotExist:
            return Response(status=404)
        if not um.voice:
            return Response({"detail":"녹음 없음"}, status=404)
        return Response({"voice_url": um.voice.url})


class MissionCompleteView(APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, mission_id):
        try:
            um = UserMission.objects.get(id=mission_id, user=request.user)
        except UserMission.DoesNotExist:
            return Response(status=404)

        mood = request.data.get('mood')  # good|fine|soso|bad
        memo = request.data.get('memo')
        photo = request.FILES.get('photo')

        if mood: um.mood = mood
        if memo: um.memo = memo
        if photo: um.photo = photo

        if um.completed and um.completed_at:
            return Response({"detail":"이미 완료된 미션입니다."}, status=409)

        um.completed = True
        um.given_up = False
        um.completed_at = timezone.now()
        um.save()

        return Response({
            "mission_id": um.id, "completed": True,
            "entry": {
                "mood": um.mood, "memo": um.memo,
                "photo_url": (um.photo.url if um.photo else None),
                "created_at": um.completed_at
            }
        })


class MissionGiveupView(APIView):
    def post(self, request, mission_id):
        try:
            um = UserMission.objects.get(id=mission_id, user=request.user)
        except UserMission.DoesNotExist:
            return Response(status=404)
        if um.completed:
            return Response({"detail":"이미 완료된 미션입니다."}, status=409)
        um.given_up = True
        um.save()
        return Response({"mission_id": um.id, "status": "GIVEN_UP"})


class LastWeekMemoriesView(APIView):
    def get(self, request):
        since = timezone.now() - timezone.timedelta(days=7)
        qs = UserMission.objects.filter(
            user=request.user,
            completed=True,
            photo__isnull=False,
            completed_at__gte=since
        ).order_by('-completed_at')

        items = [{
            "mission_id": x.id,
            "week_label": "지난 1주",
            "photo_url": x.photo.url if x.photo else None,
            "caption": (x.memo[:40] + '…') if x.memo and len(x.memo) > 40 else (x.memo or ""),
            "created_at": x.completed_at,
        } for x in qs]
        return Response({"items": items})
