from django import forms
from django.forms import ModelForm
from .models import User, Category, Product, Comment, Watchlist

class CreateForm(ModelForm):
	class Meta:
		model = Product
		fields = ["title", "description", "image_url", "category_id", "current_bid"]
		labels = {
			"title": "Title:",
			"description": "Description:",
			"image_url": "Image URL:",
			"category_id": "Category:",
			"current_bid": "Starting price:"
		}
		#body = forms.CharField(widget=forms.Textarea(attrs={'name':'body', 'rows':'3', 'cols':'5'}))
		widgets = {
			"title": forms.TextInput(attrs={
				"class": "form-control"
				}),
			"description": forms.Textarea(attrs={
				"class": "form-control",
				"rows": "3"

				}),
			"image_url": forms.URLInput(attrs={
				"class": "form-control",
				"placeholder": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQwoc-wOHrC7EoqCbHPbhQdpNOR2uDZB8tzmA&usqp=CAU"
				}),
			"category_id": forms.Select(attrs={
				"class": "form-control"
				}),
			"current_bid": forms.NumberInput(attrs={
				"class": "form-control"
				})
			}

class CommentForm(ModelForm):
	class Meta:
		model = Comment
		fields = ["content"]
		labels = {"content": ""}
		widgets = {
			"content": forms.Textarea(attrs={
				"rows": 2,
				"class": "form-control"
			})	
		}

class WatchlistForm(ModelForm):
	class Meta:
		model = Watchlist
		fields = []


class BidForm(ModelForm):
	class Meta:
		model = Product
		fields = ["current_bid"]
		labels = {"current_bid": ""}
		widgets = {
			"current_bid": forms.NumberInput(attrs={
				"class": "form-control" 		
			})
		}


class CloseForm(ModelForm):
	class Meta:
		model = Product
		fields = []