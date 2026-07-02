from django import forms
from .models import Thread, Reply, Board, Report

class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['slug', 'title', 'description']
        widgets = {
            'slug': forms.TextInput(attrs={'placeholder': 'e.g. tech, art, music (no spaces)'}),
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Technology'}),
            'description': forms.TextInput(attrs={'placeholder': 'Short description (optional)'}),
        }
        labels = {
            'slug': 'Short Name',
            'title': 'Community Title',
            'description': 'Description (optional)',
        }

    def clean_slug(self):
        slug = self.cleaned_data.get('slug', '').lower().strip()
        if not slug.isalnum():
            raise forms.ValidationError('Only letters and numbers allowed — no spaces or symbols.')
        if Board.objects.filter(slug=slug).exists():
            raise forms.ValidationError('A community with this name already exists.')
        return slug


class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['subject', 'content', 'image', 'nsfw']
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Subject (optional)'}),
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your post here...'}),
            'nsfw': forms.CheckboxInput(),
        }
        labels = {
            'subject': 'Subject',
            'content': 'Content',
            'image': 'Image (optional)',
            'nsfw': 'Mark as NSFW (blur by default)',
        }


class ReplyForm(forms.ModelForm):
    parent_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Reply
        fields = ['content', 'image', 'nsfw']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your reply here... (optional if attaching an image)'}),
            'nsfw': forms.CheckboxInput(),
        }
        labels = {
            'content': 'Reply (optional)',
            'image': 'Image (optional)',
            'nsfw': 'Mark as NSFW (blur by default)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = False

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('content') and not cleaned_data.get('image'):
            raise forms.ValidationError('A reply must have either text or an image.')
        return cleaned_data


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'details']
        widgets = {
            'details': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional details (optional)'}),
        }
        labels = {'reason': 'Reason', 'details': 'Details (optional)'}