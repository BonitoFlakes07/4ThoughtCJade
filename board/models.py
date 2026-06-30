from django.db import models

class Board(models.Model):
    slug = models.SlugField(max_length=10, unique=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['slug']

    def __str__(self):
        return f'/{self.slug}/ — {self.title}'


class Thread(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='threads')
    subject = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='thread_images/', blank=True, null=True)
    poster_id = models.CharField(max_length=16)
    created_at = models.DateTimeField(auto_now_add=True)
    bumped_at = models.DateTimeField(auto_now_add=True)
    pinned = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)

    class Meta:
        ordering = ['-pinned', '-bumped_at']

    def __str__(self):
        return self.subject or self.content[:30]

    def reply_count(self):
        return self.replies.count()


class Reply(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='reply_images/', blank=True, null=True)
    poster_id = models.CharField(max_length=16)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Reply on thread {self.thread_id}'


class Report(models.Model):
    REASON_CHOICES = [
        ('spam', 'Spam'),
        ('illegal', 'Illegal content'),
        ('harassment', 'Harassment / abuse'),
        ('off_topic', 'Off-topic / rule violation'),
        ('other', 'Other'),
    ]

    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='reports', null=True, blank=True)
    reply = models.ForeignKey(Reply, on_delete=models.CASCADE, related_name='reports', null=True, blank=True)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, default='other')
    details = models.TextField(blank=True)
    reporter_id = models.CharField(max_length=16)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        target = self.thread or self.reply
        return f'Report on {target} ({self.reason})'


class ModLog(models.Model):
    action = models.CharField(max_length=50)
    detail = models.CharField(max_length=255, blank=True)
    performed_by = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.action} by {self.performed_by}'