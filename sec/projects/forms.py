from django import forms
from .models import Project, TaskFile, TaskOffer, Delivery, ProjectCategory, Team
from django.contrib.auth.models import User
from user.models import Profile


class ProjectForm(forms.ModelForm):
    title = forms.CharField(max_length=200)
    description = forms.Textarea()
    category_id = forms.ModelChoiceField(queryset=ProjectCategory.objects.all())

    class Meta:
        model = Project
        fields = ('title', 'description', 'category_id')


class TaskFileForm(forms.ModelForm):
    file = forms.FileField()

    class Meta:
        model = TaskFile
        fields = ('file',)


class ProjectStatusForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('status',)


class TaskOfferForm(forms.ModelForm):
    title = forms.CharField(max_length=200)
    description = forms.Textarea()
    price = forms.NumberInput()

    class Meta:
        model = TaskOffer
        fields = ('title', 'description', 'price',)


class TaskOfferResponseForm(forms.ModelForm):
    feedback = forms.Textarea()

    class Meta:
        model = TaskOffer
        fields = ('status', 'feedback')


class TaskDeliveryResponseForm(forms.ModelForm):
    feedback = forms.Textarea()

    class Meta:
        model = Delivery
        fields = ('status', 'feedback')


PERMISSION_CHOICES = (
    ('Read', 'Read'),
    ('Write', 'Write'),
    ('Modify', 'Modify'),
)


class TaskPermissionForm(forms.Form):
    permission = forms.ChoiceField(choices=PERMISSION_CHOICES)

    def __init__(self, task, *args, **kwargs):
        super(TaskPermissionForm, self).__init__()
        user = User.objects.filter(pk__in=[a.user.pk for a in task.project.participants.all()])
        self.fields['user'] = forms.ModelChoiceField(queryset=user)


class DeliveryForm(forms.ModelForm):
    comment = forms.Textarea()
    file = forms.FileField()

    class Meta:
        model = Delivery
        fields = ('comment', 'file')


class TeamForm(forms.ModelForm):
    name = forms.CharField(max_length=50)

    class Meta:
        model = Team
        fields = ('name',)


class TeamAddForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(queryset=Profile.objects.all(), label='Members with read')

    class Meta:
        model = Team
        fields = ('members',)
