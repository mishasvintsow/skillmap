from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, DetailView, DeleteView
from .models import Graph, Vertex, Edge, AddEdgeForm, AddEdgeVertexForm
from itertools import zip_longest
import networkx as nx
# Create your views here.

class IndexView(TemplateView):
    template_name = 'base.html'
    
class GraphListView(ListView):
    model = Graph
    context_object_name = 'graphs'
    template_name = 'graphs.html'
    
class CreateGraph(CreateView):
    model = Graph
    fields = ['name', 'description']
    template_name = 'create_graph.html'
    
    def get_success_url(self):
        return reverse_lazy('graphs')
    
class GraphDetailView(DetailView):
    model = Graph
    template_name = 'graph_detail.html'
    context_object_name = 'graph'
    
    def get_context_data(self, **kwargs):
        self.get_object().create_image()
        context = super().get_context_data(**kwargs)
        context['edges'] = Edge.objects.filter(source__graph = self.get_object())
        return context
    
class AddVertexView(CreateView):
    model = Vertex
    fields = ['graph', 'VID', 'name', 'description']
    template_name = 'add_vertex.html'
    
    def get_initial(self):
        super(AddVertexView, self).get_initial()
        graph = Graph.objects.get(pk = self.kwargs['pk'])
        self.initial = {'graph' : graph,
                        'VID' : max(Vertex.objects.filter(graph = graph).values_list('VID', flat = True), default = 0) + 1}
        return self.initial
    
    def form_valid(self, form):
        new_vertex = form.save()
        self.reverse_pk = new_vertex.pk
        return super(AddVertexView, self).form_valid(form)
        
    
    def get_success_url(self):
        return reverse_lazy('detail_vertex', kwargs = {'pk' : self.reverse_pk})
    
class CreateIncomingView(CreateView):
    form_class = AddEdgeVertexForm
    template_name = 'add_incoming.html'
    
    def get_initial(self):
        super(CreateIncomingView, self).get_initial()
        self.vertex = Vertex.objects.get(pk = self.kwargs['pk'])
        self.initial = {'graph' : self.vertex.graph,
                        'VID' : max(Vertex.objects.filter(graph = self.vertex.graph).values_list('VID', flat = True), default = 0) + 1}
        return self.initial
    
    def form_valid(self, form):
        new_vertex = form.save()
        Edge.objects.create(source = new_vertex,
                            target = self.vertex,
                            description = form.cleaned_data['edge_description'])
        return super(CreateIncomingView, self).form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('detail_vertex', kwargs = {'pk' : self.kwargs['pk']})
    
class CreateOutcomingView(CreateView):
    form_class = AddEdgeVertexForm
    template_name = 'add_outcoming.html'
    
    def get_initial(self):
        super(CreateOutcomingView, self).get_initial()
        self.vertex = Vertex.objects.get(pk = self.kwargs['pk'])
        self.initial = {'graph' : self.vertex.graph,
                        'VID' : max(Vertex.objects.filter(graph = self.vertex.graph).values_list('VID', flat = True), default = 0) + 1}
        return self.initial
    
    def form_valid(self, form):
        new_vertex = form.save()
        Edge.objects.create(source = self.vertex,
                            target = new_vertex,
                            description = form.cleaned_data['edge_description'])
        return super(CreateOutcomingView, self).form_valid(form)
        
    def get_success_url(self):
        return reverse_lazy('detail_vertex', kwargs = {'pk' : self.kwargs['pk']})
    
        
        
    
class VertexDetailView(DetailView):
    model = Vertex
    template_name = 'vertex_detail.html'
    context_object_name = 'vertex'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        incoming_edges = self.get_object().incoming_edges.all()
        outcoming_edges = self.get_object().outcoming_edges.all()
        context['edges'] = zip_longest(incoming_edges, outcoming_edges)
        return context
    
class AddEdgeView(CreateView):
    form_class = AddEdgeForm
    template_name = 'add_edge.html'
    
    def get_success_url(self):
        return reverse_lazy('detail_graph', kwargs = {'pk' : self.kwargs['pk']})
    
    def get_form_kwargs(self):
        kwargs = super(AddEdgeView, self).get_form_kwargs()
        kwargs['pk'] = self.kwargs['pk']
        return kwargs
    
class AddIncomingEdgeView(CreateView):
    form_class = AddEdgeForm
    template_name = 'add_edge.html'
    
    def get_success_url(self):
        return reverse_lazy('detail_vertex', kwargs = {'pk' : self.kwargs['pk']})
    
    def get_form_kwargs(self):
        kwargs = super(AddIncomingEdgeView, self).get_form_kwargs()
        kwargs['pk'] = Vertex.objects.get(pk = self.kwargs['pk']).graph.pk
        return kwargs
    
    def get_initial(self):
        super(AddIncomingEdgeView, self).get_initial()
        vertex = Vertex.objects.get(pk = self.kwargs['pk'])
        self.initial = {'target' : vertex}
        return self.initial
    
    
class AddOutcomingEdgeView(CreateView):
    form_class = AddEdgeForm
    template_name = 'add_edge.html'
    
    def get_success_url(self):
        return reverse_lazy('detail_vertex', kwargs = {'pk' : self.kwargs['pk']})
    
    def get_form_kwargs(self):
        kwargs = super(AddOutcomingEdgeView, self).get_form_kwargs()
        kwargs['pk'] = Vertex.objects.get(pk = self.kwargs['pk']).graph.pk
        return kwargs
    
    def get_initial(self):
        super(AddOutcomingEdgeView, self).get_initial()
        vertex = Vertex.objects.get(pk = self.kwargs['pk'])
        self.initial = {'source' : vertex}
        return self.initial
    
    
class DeleteIncomingEdgeView(DeleteView):
    model = Edge
    template_name = 'confirm_delete_edge.html'
    
    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        self.target = self.object.target
        return super(DeleteIncomingEdgeView, self).delete(*args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('detail_vertex', kwargs = {'pk' : self.target.pk})
    
    
