from django.urls import path
from . import views
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name = 'graphs')),
    path('graphs', views.GraphListView.as_view(), name = 'graphs'),
    path('create', views.CreateGraph.as_view(), name = 'create_graph'),
    path('graph/<int:pk>', views.GraphDetailView.as_view(), name = 'detail_graph'),
    path('graph/<int:pk>/add_vertex', views.AddVertexView.as_view(), name = 'add_vertex'),
    path('graph/<int:pk>/add_edge', views.AddEdgeView.as_view(), name = 'add_edge'),
    path('vertex/<int:pk>', views.VertexDetailView.as_view(), name = 'detail_vertex'),
    path('vertex/<int:pk>/add_incoming', views.AddIncomingEdgeView.as_view(), name = 'create_incoming'),
    path('vertex/<int:pk>/add_incoming_new', views.CreateIncomingView.as_view(), name = 'create_incoming_new'),
    path('vertex/<int:pk>/add_outcoming', views.AddOutcomingEdgeView.as_view(), name = 'create_outcoming'),
    path('vertex/<int:pk>/add_outcoming_new', views.CreateOutcomingView.as_view(), name = 'create_outcoming_new'),
    path('vertex/delete_incoming/<int:pk>', views.DeleteIncomingEdgeView.as_view(), name = 'delete_incoming'),
]