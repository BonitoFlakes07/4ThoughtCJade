from django import forms
from .models import Thread, Reply

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['subject', 'content', 'image']
        widgets = {
            'subject': forms.TextInput(attrs={
                'placeholder': 'Subject (optional)',
            }),
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write your post here...',
            }),
        }
        labels = {
            'subject': 'Subject',
            'content': 'Content',
            'image': 'Image (optional)',
        }

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Write your reply here... (optional if attaching an image)',
            }),
        }
        labels = {
            'content': 'Reply (optional)',
            'image': 'Image (optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].required = False    # ← not required

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get('content')
        image = cleaned_data.get('image')

        # must have at least one of text or image
        if not content and not image:
            raise forms.ValidationError(
                'A reply must have either text or an image.'
            )
        return cleaned_data