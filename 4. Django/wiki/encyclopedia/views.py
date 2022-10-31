# MODIFY FILE 

import os
import random
import markdown2

from django import forms
from django.shortcuts import render, redirect
# Extra added #
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
from markdown2 import Markdown

from . import util

###############
### CLASSES ###
###############
class SearchForm(forms.Form):
    """
    Class created for Search forms used in Search Bar
    """
    title = forms.CharField(label='',widget=forms.TextInput(attrs={
        "class":"search",
        "placeholder":"Search Qwikipedia"
    }))

class CreateForm(forms.Form):
    """
    Class for creating new Forms
    """
    title = forms.CharField(label='',widget=forms.TextInput(attrs={
        "placeholder":"Page Title"
    }))
    text = forms.CharField(label='',widget=forms.Textarea(attrs={
        "placeholder":"Enter Page Content using Github Markdown"
    }))

class EditForm(forms.Form):
    """
    Class to edit the created Forms
    """
    text = forms.CharField(label='',widget=forms.Textarea(attrs={
        "placeholder":"Enter Page Content using Github Markdown"
    }))

#################
### FUNCTIONS ###
#################
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    """
    Display the requested entry page, if it exists
    """
    entry_md = util.get_entry(title)
    
    # Title does indeed exist, convert md to HTML and return rendered template
    if entry_md != None:
        entry_HTML = Markdown().convert(entry_md)
        return render(request, "encyclopedia/entry.html",{
            "title":title,
            "entry":entry_HTML,
            "search_form":SearchForm(),
        })
    # Title does not exist
    else: 
        related_titles = util.related_titles(title)
        return render(request, "encyclopedia/error.html",{
            "title":title,
            "related_titles":related_titles,
            "search_form":SearchForm(),
        })

def search(request):
    """
    Display the searched page, else it displays search results
    """
    # First Method: Page reached by submitting 'search' Form
    if request.method == "POST":
        form = SearchForm(request.POST)
        # If the form is valid, search for title:
        if form.is_valid():
            title = form.cleaned_data["title"]
            entry_md = util.get_entry[title]
            print('search request: ', title)
            # If entry exists, redirect to entry page
            if entry_md:
                return redirect(reverse('entry', args = [title]))
            # Else display relevant results
            else:
                related_titles = util.related_titles(title)
                return render(request, "encyclopedia/search.html", {
                    "title":title,
                    "related_titles":related_titles,
                    "search_form":SearchForm()
                })
    # Second Method: Form Invalid, return the index page:
    return redirect(reverse('index'))

def create(request):
    """
    Allow the user to create a new entry
    """
    # First Method: Reached via link, display Form
    if request.method == 'GET':
        return render(request, "encyclopedia/create.html", {
            "create_form":CreateForm(),
            "search_form":SearchForm()
        })
    # Second Method: Reached via Form submission
    elif request.method == 'POST':
        form = CreateForm(request.POST)
        # If the Form is valid, process it
        if form.is_valid():
            title = form.cleaned_data['title']
            text = form.cleaned_data['text']
        # Else, return error message
        else:
            messages.error(request, 'Entry Form not valid, please check the information!')
            return render(request,"encyclopedia/create.html",{
                "create_form":form,
                "search_form":SearchForm()
            })
        # Check the title is unique
        if util.get_entry(title):
            messages.error(request,'This page already exists, please refer to the appropiate page and edit it if any change is required')
            return render(request, "encyclopedia/create.html",{
                "create_form":form,
                "search_form":SearchForm()
            })
        # Else save new title and redirect to new page
        else:
            util.save_entry(title,text)
            messages.success(request,f'New page "{title}" created succesfully')
            return redirect(reverse('entry', args = [title]))

def edit(request,title):
    """
    Allow the user to edit existing entry page
    """
    # First Method: Reached via link, return Form with existing entry
    if request.method == 'GET':
        text = util.get_entry(title)
        # If title does not exist, return to the index page with error
        if text == None:
            messages.error(request, f'"{title}" page does not exist, please create it before trying to edit')
        # Else return Form with existing info
        else:
            return render(request, "encyclopedia/edit.html", {
                "title":title,
                "edit_form":EditForm(initial={
                    'text':text
                }),
                "search_form":SearchForm()
            })
    # Second Method: Reached via posting Form, update page and redirect
    elif request.method == 'POST':
        form = EditForm(request.POST)
        # Check if the Form is valid
        if form.is_valid():
            text = form.cleaned_data['text']
            util.save_entry(title,text)
            messages.success(request, f'Entry "{title}" updated in a succesful manner')
            return redirect(reverse('entry', args = [title]))
        # If Form is invalid
        else:
            messages.error(request, f'Editing Form is not valid, please try again')
            return render(request, "encyclopedia/edit.html", {
                "title":title,
                "edit_form":form,
                "search_form":SearchForm()
            })

def random_title(request):
    """
    Redirect user to random page
    """
    # Get list of titles, obtain a random one
    titles = util.list_entries()
    title = random.choice(titles)
    # Redirect to selected page
    return redirect(reverse('entry', args = [title]))