import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models

from user.models import Profile


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length):
        """Returns a filename that's free on the target storage system, and
        available for new content to be written to.

        Found at http://djangosnippets.org/snippets/976/

        This file storage solves overwrite on upload problem. Another
        proposed solution was to override the save method on the model
        like so (from https://code.djangoproject.com/ticket/11663):

        def save(self, *args, **kwargs):
            try:
                this = MyModelName.objects.get(id=self.id)
                if this.MyImageFieldName != self.MyImageFieldName:
                    this.MyImageFieldName.delete()
            except: pass
            super(MyModelName, self).save(*args, **kwargs)
        """
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name


class ProjectCategory(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Project(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
    participants = models.ManyToManyField(Profile, related_name='project_participants')
    category = models.ForeignKey(ProjectCategory, on_delete=models.CASCADE, related_name='project_category')

    OPEN = 'o'
    INPROG = 'i'
    FINISHED = 'f'
    STATUS_CHOICES = (
        (OPEN, 'Open'),
        (INPROG, 'In progress'),
        (FINISHED, 'Finished'),
    )
    status = models.CharField(max_length=11, choices=STATUS_CHOICES, default=OPEN)

    def __str__(self):
        return self.title


class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=500)
    budget = models.IntegerField(default=0)

    AWAITING_DELIVERY = 'ad'
    PENDING_ACCEPTANCE = 'pa'
    PENDING_PAYMENT = 'pp'
    PAYMENT_SENT = 'ps'
    DECLINED_DELIVERY = 'dd'
    STATUS_CHOICES = (
        (AWAITING_DELIVERY, 'Waiting for delivery'),
        (PENDING_ACCEPTANCE, 'Delivered and waiting for acceptance'),
        (PENDING_PAYMENT, 'Delivery has been accepted, awaiting payment'),
        (PAYMENT_SENT, 'Payment for delivery is done'),
        (DECLINED_DELIVERY, 'Declined delivery, please revise'),
    )

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=AWAITING_DELIVERY)
    feedback = models.TextField(max_length=500, default="")

    read = models.ManyToManyField(Profile, related_name='task_participants_read')
    write = models.ManyToManyField(Profile, related_name='task_participants_write')
    modify = models.ManyToManyField(Profile, related_name='task_participants_modify')

    def __str__(self):
        return str(self.id) + " " + self.title

    def accepted_task_offer(task):
        task_offer = None
        try:
            task_offer = task.taskoffer_set.get(status='a')
        except TaskOffer.DoesNotExist:
            pass
        return task_offer


class Team(models.Model):
    name = models.CharField(max_length=200)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="teams")
    members = models.ManyToManyField(Profile, related_name='teams')
    write = models.BooleanField(default=False)

    def __str__(self):
        return self.task.project.title + " - " + self.task.title + " - " + self.name


def directory_path(instance, filename):
    return 'uploads/tasks/{0}/{1}'.format(instance.task.id, filename)


class TaskFile(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="files")
    file = models.FileField(upload_to=directory_path, storage=OverwriteStorage())

    def name(self):
        parts = self.file.path.split("/")
        file_name = parts[len(parts) - 1]
        return file_name

    def get_task(self):
        return self.task


class TaskFileTeam(models.Model):
    file = models.ForeignKey(TaskFile, on_delete=models.CASCADE, related_name="teams")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="file")
    name = models.CharField(max_length=200)
    read = models.BooleanField(default=False)
    write = models.BooleanField(default=False)
    modify = models.BooleanField(default=False)


class Delivery(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="delivery")
    file = models.FileField(upload_to=directory_path)
    comment = models.TextField(max_length=500)
    delivery_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="deliveries")
    delivery_time = models.DateTimeField(auto_now=True)
    responding_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="responded_deliveries",
                                        blank=True, null=True)
    responding_time = models.DateTimeField(blank=True, null=True)

    ACCEPTED = 'a'
    PENDING = 'p'
    DECLINED = 'd'
    STATUS_CHOICES = (
        (ACCEPTED, 'Accepted'),
        (PENDING, 'Pending'),
        (DECLINED, 'Declined'),
    )
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=PENDING)
    feedback = models.TextField(max_length=500)


class TaskOffer(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    offerer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    price = models.IntegerField(default=0)
    description = models.TextField(max_length=500)

    ACCEPTED = 'a'
    PENDING = 'p'
    DECLINED = 'd'
    STATUS_CHOICES = (
        (ACCEPTED, 'Accepted'),
        (PENDING, 'Pending'),
        (DECLINED, 'Declined'),
    )
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default=PENDING)
    feedback = models.TextField(max_length=500)
