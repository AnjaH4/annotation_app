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


class Participant(models.Model):
    ppant_id = models.CharField(max_length=20)
    prolificID = models.CharField(max_length=30)
    time_started = models.CharField(max_length=40) #Y not use DateTimeField?
    list_one = models.CharField(max_length=8,choices=(('three','three'),('four','four')),default='three')
    list_two = models.CharField(max_length=8,choices=(('three','three'),('four','four')),default='three')
    CATEGORY_CHOICES = (('A','no assistance'), ('B', 'just familiar'), ('C', 'intro help'))
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default='C')
    def __str__(self):
        return self.ppant_id


class Response(models.Model):
    time_at_submission = models.CharField(max_length=40)
    response_id = models.CharField(max_length=20)
    ppant_id = models.ForeignKey(Participant, on_delete=models.CASCADE)
    image_id = models.CharField(max_length=20)
    choice=models.CharField(max_length=20)  # 'left' or 'right'
    confidence=models.CharField(max_length=20)
    inconsistency_type=models.CharField(max_length=50, choices=[
        ('color', 'Color'),
        ('boundary', 'Boundary'),
        ('texture', 'Texture'),
        ('geometry', 'Geometry'),
        ('landmark', 'Landmark')
    ], default='color')
    reasoning=models.CharField(blank=True,max_length=500)
    heatmapFill = models.CharField(blank=True,max_length=500)
    is_correct = models.BooleanField(default=False)  # Track if the user's answer was correct
    def __str__(self):
        return self.response_id


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
