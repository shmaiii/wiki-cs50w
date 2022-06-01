from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect, Http404
import markdown
from . import util
import random
from django.contrib import messages
from django.urls import reverse

import encyclopedia


class NewQueryForm(forms.Form):
    searchEntry = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': "Search Encyclopedia"}))

class NewPageForm(forms.Form):
    title = forms.CharField(label="TITLE")
    content = forms.CharField(widget=forms.Textarea(attrs={"rows": 8, "cols": 20}), label="MARKDOWN CONTENT")

class EditPageForm(forms.Form):        
    content = forms.CharField(widget=forms.Textarea(attrs={"rows": 8, "cols": 20}), label="")


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": NewQueryForm()
    })

# render a page that displays the contents of the title entry
# if entry not exists, error page 404 
def wiki(request, title):
    mdFile = util.get_entry(title)

    if mdFile == None:
        #raise Http404("This entry does not exist!")
        return render(request, "encyclopedia/errorNotFound.html")
    else:
        htmlContent = markdown.markdown(mdFile)

        return render(request, "encyclopedia/entry.html", {
            "content": htmlContent,
            "title": title,
            "form": NewQueryForm()
        })

#if form is valid, take data and see if the entry exists, if it is use wiki to render the page
#if no such entry, check substring, capitalization, or no results
def search(request):
    if request.method == "POST":
        form = NewQueryForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["searchEntry"]
            if query in util.list_entries():
                return wiki(request, query)
                #return HttpResponseRedirect(f"wiki/{query}")
            else: 
                entriesPresent = []
                for entry in util.list_entries():
                    if query.upper() in entry.upper():
                        entriesPresent.append(entry)
                
                if len(entriesPresent) == 0:
                    return render(request, "encyclopedia/entry.html", {
                        "content": '<h1> Results Not Found </h1>',
                        "title": query,
                        "form": NewQueryForm()
                    })
                else:
                    return render(request, "encyclopedia/index.html", {
                        "entries": entriesPresent,
                        "form": NewQueryForm()
                    })
        else:
            return render(request, "encyclopedia/index.html", {
                "form": form
            })
        

    return render(request, "encyclopedia/index.html", {
        "form": NewQueryForm()
    })

def randomPage(request):
    index = random.randint(0, len(util.list_entries()) - 1)
    entry = util.list_entries()[index]
    return HttpResponseRedirect(reverse('wiki', kwargs={'title': entry}))

#if method is POST and form is valid, take data of title and mdContent. 
#if title is in list of entries, error pop up message; otherwise, save new entry 
def newPage(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            mdContent = form.cleaned_data["content"]
            
            if title in util.list_entries():
                messages.error(request, 'The entry with this title already exists!')
            else: 
                util.save_entry(title, mdContent)
                return HttpResponseRedirect(reverse('wiki', kwargs={'title': title}))
                
    return render(request, "encyclopedia/createNewPage.html", {
        "form": NewQueryForm(),
        "newPageForm": NewPageForm()
    })

# if no post method request is sent, render the edit page with the existing content set as initial through a dictionary
# if post method is detected, modifies and resave the entry based on the submitted content
def editPage(request, title):
    initialDict = {
        "content": util.get_entry(title)
    }

    if request.method == "POST":
        form = EditPageForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse('wiki', kwargs={"title": title}))

    return render(request, "encyclopedia/editPage.html", {
        "form": NewQueryForm(),
        "title": title,
        "editForm": EditPageForm(initial = initialDict)
    })