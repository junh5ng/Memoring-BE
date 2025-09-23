from rest_framework import serializers
from .models import Mission, UserMission


class MissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mission
        fields = ['id', 'content']


class UserMissionCurrentSerializer(serializers.ModelSerializer):
    
    # 제목/설명은 Mission의 content를 재사용
    title = serializers.CharField(source='mission.content', read_only=True)
    description = serializers.CharField(source='mission.content', read_only=True)  # 프로토타입: content 재사용
    
    # 모델 속성 그대로 노출
    voice_uploaded = serializers.SerializerMethodField()
    listenable = serializers.SerializerMethodField()
    # status 추가
    status = serializers.CharField(source="status", read_only=True)

    class Meta:
        model = UserMission
        fields = [
            'id','title','description','scheduled_at','alarm_offset_minutes',
            'voice_uploaded','completed','listenable',
            'status', # 추가
        ]

    def get_voice_uploaded(self, obj): return bool(obj.voice)
    def get_listenable(self, obj): return bool(obj.voice)