import os

from django.db import models
import subprocess

# Create your models here.
class MediaFile(models.Model):
    file = models.FileField(upload_to='chat_media/', blank=True, null=True, max_length=1000)
    thumb = models.FileField(upload_to='video_thumb/', blank=True, null=True, max_length=1000)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id) + ": " + str(self.file)

    # def save(self, *args, **kwargs):
    #     subprocess.call(['ffmpeg', '-i', os.path.basename(self.file.name), '-ss', '00:00:00.000', '-vframes', '1',  'chat_media/output.jpg'])
    #     super().save(*args, **kwargs)
