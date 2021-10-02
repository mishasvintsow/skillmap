from itertools import groupby

from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import ModelForm
from django.forms.models import ModelChoiceIterator, inlineformset_factory

from domain.models import Strategy, Action, Domain


class StrategyIterator(ModelChoiceIterator):
    def __init__(self, domain_code, *args, **kwargs):
        #domain_code = kwargs.pop('domain_code', None)
        print("====================================================================")
        print(domain_code)
        print("====================================================================")
        self.queryset = Strategy.objects.filter(skill_goal__domain=Domain.objects.get(code=domain_code))
        super(StrategyIterator, self).__init__(*args, **kwargs)

    def __iter__(self):
        queryset = self.queryset.select_related('skill_goal').order_by('skill_goal__code', 'code')
        groups = groupby(queryset, key=lambda x: x.skill_goal)
        for skill_goal, strategies in groups:
            yield [
                skill_goal.name,
                [
                    (strategy.id, strategy.name)
                    for strategy in strategies
                ]
            ]


class ActionForm(ModelForm):
    class Meta:
        model = Action
        fields = ['order', 'description', 'prerequisites']
        widgets = {
            'prerequisites': FilteredSelectMultiple("verbose name", is_stacked=True, attrs={'size': 12})
        }

    def __init__(self, domain_code, *args, **kwargs):
        #domain_code = Domain.objects.get(code=kwargs.pop('domain_code', None))
        super(ActionForm, self).__init__(*args, **kwargs)
        self.fields['prerequisites'].choices = StrategyIterator(domain_code=domain_code, field=self.fields['prerequisites'])


ActionsFormSet = inlineformset_factory(Strategy, Action, form=ActionForm, extra=1)
