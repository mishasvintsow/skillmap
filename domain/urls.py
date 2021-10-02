from django.urls import path
from . import views

urlpatterns = [
    path('', views.DomainListView.as_view(), name='domains'),
    path('add', views.DomainCreateView.as_view(), name='domain_create'),
    path('<int:domain_code>', views.DomainDetailView.as_view(), name='domain_detail'),
    path('<int:domain_code>/edit', views.DomainUpdateView.as_view(), name='domain_update'),
    path('<int:domain_code>/skill/add', views.SkillCreateView.as_view(), name='skill_create'),
    path('<int:domain_code>/skill/<int:skill_code>', views.SkillDetailView.as_view(), name='skill_detail'),
    path('<int:domain_code>/skill/<int:skill_code>/edit', views.SkillUpdateView.as_view(), name='skill_update'),
    path('<int:domain_code>/skill/<int:skill_code>/strategy/add',
         views.StrategyCreateView.as_view(), name='strategy_create'),
    path('<int:domain_code>/skill/<int:skill_code>/strategy/<int:strategy_code>',
         views.StrategyDetailView.as_view(), name='strategy_detail'),
    path('<int:domain_code>/skill/<int:skill_code>/strategy/<int:strategy_code>/edit',
         views.StrategyUpdateView.as_view(), name='strategy_update'),
]
