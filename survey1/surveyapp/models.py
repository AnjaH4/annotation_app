from django.db import models


# class Image(models.Model):
#     image_id = models.CharField(max_length=20)
#     filename = models.CharField(max_length=20)
#     def __str__(self):
#         return self.image_id

class Image(models.Model):
    image_id = models.CharField(max_length=20, unique=True)  # Example: "065_0"
    fake_path = models.CharField(max_length=255, null=True, blank=True)  # Path to fake image (nullable)
    real_path = models.CharField(max_length=255, null=True, blank=True)  # Path to real image (nullable)
    times_seen = models.IntegerField(default=0)  # Tracks how often the pair has been shown

    def __str__(self):
        return f"{self.image_id} (Seen: {self.times_seen} times)"

    class Meta:
        indexes = [
            models.Index(fields=['image_id']),
        ]

class AttentionTestImage(models.Model):
    image_id = models.CharField(max_length=20, unique=True)  # Example: "065_0"
    fake_path = models.CharField(max_length=255, null=True, blank=True)  # Path to fake image (nullable)
    real_path = models.CharField(max_length=255, null=True, blank=True)  # Path to real image (nullable)
    times_seen = models.IntegerField(default=0)  # Tracks how often the pair has been shown

    def __str__(self):
        return f"{self.image_id} (Seen: {self.times_seen} times)"

    class Meta:
        indexes = [
            models.Index(fields=['image_id']),
        ]


class Participant(models.Model):
    ppant_id = models.CharField(max_length=20)
    time_started = models.CharField(max_length=40) #Y not use DateTimeField?

    def __str__(self):
        return self.ppant_id


class Response(models.Model):
    ppant_id = models.ForeignKey(Participant, on_delete=models.CASCADE)
    time_at_submission = models.DateTimeField()
    time_start = models.CharField(max_length=20)
    response_id = models.CharField(max_length=20)
    image_id = models.CharField(max_length=255)
    choice = models.CharField(max_length=10)  # 'left' or 'right'
    confidence = models.IntegerField()
    heatmapFill = models.JSONField(default=list)  # Use JSONField for lists
    assigned_label = models.IntegerField()  # 1 for selected, 0 for unselected
    gt = models.IntegerField()  # 1 for fake, 0 for real
    inconsistency_color = models.IntegerField(default=0)
    inconsistency_boundary = models.IntegerField(default=0)
    inconsistency_landmark = models.IntegerField(default=0)
    inconsistency_texture = models.IntegerField(default=0)
    position = models.CharField(max_length=5)  # 'left' or 'right'
    is_correct = models.BooleanField(default=False)



class AdviceStartTime(models.Model):
    ppant_id = models.ForeignKey(Participant, on_delete=models.CASCADE)
    advice_type = models.CharField(max_length=20)
    time_at_submission = models.CharField(max_length=40)
    def __str__(self):
        return self.ppant_id


class AdviceEndTime(models.Model):
    ppant_id = models.ForeignKey(Participant, on_delete=models.CASCADE)
    advice_type = models.CharField(max_length=20)
    time_at_submission = models.CharField(max_length=40)
    def __str__(self):
        return self.ppant_id
