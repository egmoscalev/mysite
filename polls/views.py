from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    '''
    SELECT polls_question.id, polls_question.question_text 
    FROM 
    polls_question RIGHT JOIN polls_choice ON polls_choice.question_id = polls_question.id
    GROUP BY polls_question.id;
    '''

    #questions with no choices are not displayed
    #and questions with pub_date set in future are not displayed
    #unless the user is superuser
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Question.objects.order_by("-pub_date")[:5]
        return Question.objects.filter(choice__isnull=False).filter(pub_date__lte=timezone.now()).distinct().order_by("-pub_date")[:5]
    

class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"
    context_object_name = "question"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = Question.objects.get(pk = self.kwargs['pk'])
        
        #questions with no choices are not displayed
        #and questions with pub_date set in future are not displayed
        #unless the user is superuser
        if not self.request.user.is_superuser:

            if not question.has_choices():
                raise Http404
            
            if not question.was_published_already():
                raise Http404

        return context

class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"
    context_object_name = "question"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = Question.objects.get(pk = self.kwargs['pk'])

        #questions with no choices are not displayed
        #and questions with pub_date set in future are not displayed
        #unless the user is superuser
        if not self.request.user.is_superuser:

            if not question.has_choices():
                raise Http404
            
            if not question.was_published_already():
                raise Http404
        

        return context

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    user = request.user

    #questions with no choices are not displayed
    #and questions with pub_date set in future are not displayed
    #unless the user is superuser
    if not user.is_superuser:
        if not question.has_choices():
            raise Http404
        
        #questions with pub_date set in future are not displayed
        if not question.was_published_already():
            raise Http404

    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {"question": question, "error_message": "you didn't select a choice",}
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


