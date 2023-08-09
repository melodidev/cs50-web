from django.shortcuts import render
from . import util

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import random
import markdown2

class SearchForm(forms.Form):
	q = forms.CharField(label="Search")

class EntryTitleForm(forms.Form):
	entry_title = forms.CharField(label="EntryTitle")

class EntryContentForm(forms.Form):
	entry_content = forms.CharField(label="EntryContent")

def index(request):
	return render(request, "encyclopedia/index.html", {
		"entries": util.list_entries()
	})

def title(request, title):
	entries = util.list_entries()

	if title in entries:
		return render(request, "encyclopedia/title.html", {
			"title": title,
			"entry": markdown2.markdown(util.get_entry(title))
		})
	return render(request, "encyclopedia/error.html", {
				"error": "Page not found."
		})

def search(request):
	# Get user input
	if request.method == "POST":
		form = SearchForm(request.POST)
		if form.is_valid():
			user_input = form.cleaned_data["q"]
			# If user input in entry list, go to that page
			results = []
			entries = util.list_entries()
			for entry in entries:
				if entry.lower() == user_input.lower():
					return HttpResponseRedirect(reverse("wiki:title", args=[user_input]))
				# If user input is a part of entry, list them
				elif user_input.lower() in entry.lower():
					results.append(entry)
		try:
			return render(request, "encyclopedia/search.html", {
				"results": results
			})
		except:
			return render(request, "encyclopedia/error.html", {
				"error": "Invalid user input."
			})

def create(request):
	if request.method == "POST":
		form1 = EntryTitleForm(request.POST)
		form2 = EntryContentForm(request.POST)
		if form1.is_valid() and form2.is_valid():
			entry_title = form1.cleaned_data["entry_title"]
			entry_content = form2.cleaned_data["entry_content"]
			# If entry title is already exist, present an error message
			entries = util.list_entries()
			if entry_title.lower() in [entry.lower() for entry in entries]:
				return render(request, "encyclopedia/error.html", {
					"error": "Page already exists."
				})
			# Else save the page, and go to the new page
			util.save_entry(entry_title, entry_content)
			return HttpResponseRedirect(reverse("wiki:title", args=[entry_title]))

	return render(request, "encyclopedia/create.html")

def edit(request, title):
	if request.method == "POST":
		form = EntryContentForm(request.POST)
		if form.is_valid():
			entry_content = form.cleaned_data["entry_content"]
			util.save_entry(title, entry_content)
			return HttpResponseRedirect(reverse("wiki:title", args=[title]))

	return render(request, "encyclopedia/edit.html", {
		"title": title,
		"entry": util.get_entry(title)
	})

# Returns a random page
def random_page(request):
	# Get a list of all entries
	entry_list = util.list_entries()
	# Randomly select one title
	title = random.choice(entry_list)
	return HttpResponseRedirect(reverse("wiki:title", args=[title]))