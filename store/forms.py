from django import forms
from .models import ReviewRating

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']


class PriceRangeForm(forms.Form):
    min_price = forms.ChoiceField(
        required=False,
        choices=[(0, '$0'), (50, '$50'), (100, '$100'), (150, '$150'), (200, '$200'), (500, '$500'), (1000, '$1000')],
        widget=forms.Select(attrs={'class': 'mr-2 form-control'})
    )
    
    max_price = forms.ChoiceField(
        required=False,
        choices=[(50, '$50'), (100, '$100'), (150, '$150'), (200, '$200'), (500, '$500'), (1000, '$1000'), (2000, '$2000'), (2500, '$2500'), (3000, '$3000')],
        widget=forms.Select(attrs={'class': 'mr-2 form-control'})
    )