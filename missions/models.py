from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


def voice_upload_to(instance, filename):
    return f"missions/{instance.user_id}/{instance.id or 'new'}/voice/{filename}"

def photo_upload_to(instance, filename):
    return f"missions/{instance.user_id}/{instance.id or 'new'}/photo/{filename}"


class Mission(models.Model):
    # 후보 미션 텍스트(홈에서 3개 미션 제공)
    content = models.TextField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        text = self.content or ""
        return (text[:30] + "…") if len(text) > 30 else text

class UserMission(models.Model):
    class Mood(models.TextChoices):
        GOOD = 'good', '좋음'
        FINE = 'fine', '양호'
        SOSO = 'soso', '보통'
        BAD  = 'bad',  '나쁨'

    # 추가 － 상태 상수 (문자열은 응답에 그대로 쓰임)
    class MissionStatus(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "진행 중"
        COMPLETED   = "COMPLETED",   "완료"
        GIVEN_UP    = "GIVEN_UP",    "포기"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='missions')
    mission = models.ForeignKey(Mission, on_delete=models.PROTECT, related_name='user_missions')

    # 일정/알림
    scheduled_at = models.DateTimeField(null=True, blank=True)
    alarm_offset_minutes = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(720)],
        help_text="알림 시각 = scheduled_at - offset(분)"
    )

    # 녹음(재녹음 시 덮어쓰기)
    voice = models.FileField(upload_to=voice_upload_to, null=True, blank=True)

    # 일지 (감정, 메모, 사진)
    mood = models.CharField(max_length=10, choices=Mood.choices, null=True, blank=True)
    memo = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to=photo_upload_to, null=True, blank=True)

    # 상태 (완료, 포기)
    completed = models.BooleanField(default=False)
    given_up = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    # 조회/정렬용
    created_at = models.DateTimeField(auto_now_add=True)  # 미션 선택(생성) 시각
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=~(models.Q(completed=True) & models.Q(given_up=True)),
                name='completed_xor_givenup'
            )
        ]

    def __str__(self):
        state = "포기" if self.given_up else ("완료" if self.completed else "진행 중")
        return f"[{self.user.username}] {self.mission_id} ({state})"
    
    @property
    def voice_uploaded(self): return bool(self.voice)

    @property
    def listenable(self): return self.voice_uploaded

    # 추가 - DB 스키마 안 바꾸고 상태를 계산해서 노출
    @property
    def status(self) -> str:
        if self.given_up:
            return self.MissionStatus.GIVEN_UP
        if self.completed:
            return self.MissionStatus.COMPLETED
        return self.MissionStatus.IN_PROGRESS