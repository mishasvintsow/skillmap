# Create your views here.
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from domain.forms import ActionsFormSet
from domain.models import Domain, Skill, Strategy


class DomainListView(ListView):
    model = Domain
    context_object_name = 'domains'
    template_name = 'domain/domains.html'


class DomainDetailView(DetailView):
    model = Domain
    context_object_name = 'domain'
    template_name = 'domain/domain_detail.html'

    def get_object(self):
        return get_object_or_404(Domain, code=self.kwargs['domain_code'])


class DomainCreateView(CreateView):
    model = Domain
    fields = ['name', 'description']
    template_name = 'domain/domain_create.html'

    def get_success_url(self, **kwargs):
        return reverse_lazy("domain_detail", args=(self.object.code,))


class DomainUpdateView(UpdateView):
    model = Domain
    fields = ['name', 'description']
    context_object_name = 'domain'
    template_name = 'domain/domain_update.html'

    def get_object(self):
        return get_object_or_404(Domain, code=self.kwargs['domain_code'])

    def get_success_url(self, **kwargs):
        return reverse_lazy("domain_detail", args=(self.object.code,))


class SkillCreateView(CreateView):
    model = Skill
    fields = ['domain', 'name', 'description']
    template_name = 'domain/skill_create.html'

    def get_initial(self):
        initial = super(SkillCreateView, self).get_initial()
        initial['domain'] = get_object_or_404(Domain, code=self.kwargs['domain_code'])
        return initial

    def get_success_url(self, **kwargs):
        return reverse_lazy("skill_detail", args=(self.object.domain.code, self.object.code,))


class SkillDetailView(DetailView):
    model = Skill
    context_object_name = 'skill'
    template_name = 'domain/skill_detail.html'

    def get_object(self):
        domain = get_object_or_404(Domain, code=self.kwargs['domain_code'])
        return get_object_or_404(Skill, domain=domain, code=self.kwargs['skill_code'])


class SkillUpdateView(UpdateView):
    model = Skill
    fields = ['name', 'description']
    context_object_name = 'skill'
    template_name = 'domain/skill_update.html'

    def get_object(self):
        domain = get_object_or_404(Domain, code=self.kwargs['domain_code'])
        return get_object_or_404(Skill, domain=domain, code=self.kwargs['skill_code'])

    def get_success_url(self, **kwargs):
        return reverse_lazy("skill_detail", args=(self.object.domain.code, self.object.code,))


class StrategyCreateView(CreateView):
    model = Strategy
    fields = ['skill_goal', 'name', 'problem']
    template_name = 'domain/strategy_create.html'

    def get_initial(self):
        initial = super(StrategyCreateView, self).get_initial()
        domain = get_object_or_404(Domain, code=self.kwargs['domain_code'])
        initial['skill_goal'] = get_object_or_404(Skill, domain=domain, code=self.kwargs['skill_code'])
        return initial

    def get_success_url(self, **kwargs):
        return reverse_lazy("strategy_update", args=(self.object.skill_goal.domain.code,
                                                     self.object.skill_goal.code,
                                                     self.object.code,))


class StrategyDetailView(DetailView):
    model = Strategy
    context_object_name = 'strategy'
    template_name = 'domain/strategy_detail.html'

    def get_object(self):
        domain = get_object_or_404(Domain, code=self.kwargs['domain_code'])
        skill = get_object_or_404(Skill, domain=domain, code=self.kwargs['skill_code'])
        return get_object_or_404(Strategy, skill_goal=skill, code=self.kwargs['strategy_code'])


class StrategyUpdateView(UpdateView):
    model = Strategy
    context_object_name = 'strategy'
    fields = ['name', 'problem']
    template_name = 'domain/strategy_actions_update.html'

    def get_object(self):
        domain = get_object_or_404(Domain, code=self.kwargs['domain_code'])
        skill = get_object_or_404(Skill, domain=domain, code=self.kwargs['skill_code'])
        return get_object_or_404(Strategy, skill_goal=skill, code=self.kwargs['strategy_code'])

    def get_success_url(self, **kwargs):
        return reverse_lazy("strategy_update", args=(self.object.skill_goal.domain.code,
                                                     self.object.skill_goal.code,
                                                     self.object.code,))

    #    def get_form_kwargs(self):
    #        kwargs = super(StrategyUpdateView, self).get_form_kwargs()
    #        kwargs.update({
    #            'domain_code': self.kwargs['domain_code']
    #        })
    #        return kwargs

    def get_context_data(self, **kwargs):
        context = super(StrategyUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['formset'] = ActionsFormSet(self.request.POST, instance=self.object,
                                                form_kwargs={'domain_code': self.object.skill_goal.domain.code})
            context['formset'].full_clean()
        else:
            context['formset'] = ActionsFormSet(instance=self.object,
                                                form_kwargs={'domain_code': self.object.skill_goal.domain.code})
            print(context['formset'])
        return context

    def form_valid(self, form):
        context = self.get_context_data(form=form)
        formset = context['formset']
        if formset.is_valid():
            response = super().form_valid(form)
            formset.instance = self.object
            formset.save()
            return response
        else:
            return super().form_invalid(form)
