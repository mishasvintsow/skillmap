from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, DetailView, DeleteView, FormView
from .models import Graph, Vertex, Edge, AddEdgeForm, AddEdgeVertexForm, GraphFromJSONForm, TopSortForm
from itertools import zip_longest
import networkx as nx
import json
from django.http import Http404
from networkx.algorithms.dag import topological_sort
from django.views.generic.base import RedirectView
from django.db.models import Count


# Create your views here.


class GraphListView(ListView):
    model = Graph
    context_object_name = 'graphs'
    template_name = 'graph/graphs.html'


class CreateGraph(CreateView):
    model = Graph
    fields = ['name', 'description']
    template_name = 'graph/create_graph.html'

    def get_success_url(self):
        return reverse_lazy('graphs')


class GraphDetailView(DetailView):
    model = Graph
    template_name = 'graph/graph_detail.html'
    context_object_name = 'graph'

    def get_context_data(self, **kwargs):
        self.get_object().create_image()
        context = super().get_context_data(**kwargs)
        context['edges'] = Edge.objects.filter(source__graph=self.get_object())
        return context


class AddVertexView(CreateView):
    model = Vertex
    fields = ['graph', 'VID', 'name', 'description']
    template_name = 'graph/add_vertex.html'

    def get_initial(self):
        super(AddVertexView, self).get_initial()
        graph = Graph.objects.get(pk=self.kwargs['pk'])
        self.initial = {'graph': graph,
                        'VID': max(Vertex.objects.filter(graph=graph).values_list('VID', flat=True), default=0) + 1}
        return self.initial

    def form_valid(self, form):
        new_vertex = form.save()
        self.reverse_pk = new_vertex.pk
        return super(AddVertexView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('detail_vertex', kwargs={'pk': self.reverse_pk})


class CreateIncomingView(CreateView):
    form_class = AddEdgeVertexForm
    template_name = 'graph/add_incoming.html'

    def get_initial(self):
        super(CreateIncomingView, self).get_initial()
        self.vertex = Vertex.objects.get(pk=self.kwargs['pk'])
        self.initial = {'graph': self.vertex.graph,
                        'VID': max(Vertex.objects.filter(graph=self.vertex.graph).values_list('VID', flat=True),
                                   default=0) + 1}
        return self.initial

    def form_valid(self, form):
        new_vertex = form.save()
        Edge.objects.create(source=new_vertex,
                            target=self.vertex,
                            description=form.cleaned_data['edge_description'])
        return super(CreateIncomingView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('detail_vertex', kwargs={'pk': self.kwargs['pk']})


class CreateOutcomingView(CreateView):
    form_class = AddEdgeVertexForm
    template_name = 'graph/add_outcoming.html'

    def get_initial(self):
        super(CreateOutcomingView, self).get_initial()
        self.vertex = Vertex.objects.get(pk=self.kwargs['pk'])
        self.initial = {'graph': self.vertex.graph,
                        'VID': max(Vertex.objects.filter(graph=self.vertex.graph).values_list('VID', flat=True),
                                   default=0) + 1}
        return self.initial

    def form_valid(self, form):
        new_vertex = form.save()
        Edge.objects.create(source=self.vertex,
                            target=new_vertex,
                            description=form.cleaned_data['edge_description'])
        return super(CreateOutcomingView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('detail_vertex', kwargs={'pk': self.kwargs['pk']})


class VertexDetailView(DetailView):
    model = Vertex
    template_name = 'graph/vertex_detail.html'
    context_object_name = 'vertex'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        incoming_edges = self.get_object().incoming_edges.all()
        outcoming_edges = self.get_object().outcoming_edges.all()
        context['edges'] = zip_longest(incoming_edges, outcoming_edges)
        return context


class AddEdgeView(CreateView):
    form_class = AddEdgeForm
    template_name = 'graph/add_edge.html'

    def get_success_url(self):
        return reverse_lazy('detail_graph', kwargs={'pk': self.kwargs['pk']})

    def get_form_kwargs(self):
        kwargs = super(AddEdgeView, self).get_form_kwargs()
        kwargs['pk'] = self.kwargs['pk']
        return kwargs


class AddIncomingEdgeView(CreateView):
    form_class = AddEdgeForm
    template_name = 'graph/add_edge.html'

    def get_success_url(self):
        return reverse_lazy('detail_vertex', kwargs={'pk': self.kwargs['pk']})

    def get_form_kwargs(self):
        kwargs = super(AddIncomingEdgeView, self).get_form_kwargs()
        kwargs['pk'] = Vertex.objects.get(pk=self.kwargs['pk']).graph.pk
        return kwargs

    def get_initial(self):
        super(AddIncomingEdgeView, self).get_initial()
        vertex = Vertex.objects.get(pk=self.kwargs['pk'])
        self.initial = {'target': vertex}
        return self.initial


class AddOutcomingEdgeView(CreateView):
    form_class = AddEdgeForm
    template_name = 'graph/add_edge.html'

    def get_success_url(self):
        return reverse_lazy('detail_vertex', kwargs={'pk': self.kwargs['pk']})

    def get_form_kwargs(self):
        kwargs = super(AddOutcomingEdgeView, self).get_form_kwargs()
        kwargs['pk'] = Vertex.objects.get(pk=self.kwargs['pk']).graph.pk
        return kwargs

    def get_initial(self):
        super(AddOutcomingEdgeView, self).get_initial()
        vertex = Vertex.objects.get(pk=self.kwargs['pk'])
        self.initial = {'source': vertex}
        return self.initial


class DeleteIncomingEdgeView(DeleteView):
    model = Edge
    template_name = 'graph/confirm_delete_edge.html'

    def delete(self, *args, **kwargs):
        self.object = self.get_object()
        self.target = self.object.target
        return super(DeleteIncomingEdgeView, self).delete(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('detail_vertex', kwargs={'pk': self.target.pk})


class GraphToJSONView(DetailView):
    model = Graph
    template_name = "graph/graph_to_JSON.html"
    context_object_name = "graph"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        g = self.get_object()
        d = {'name': g.name,
             'description': g.description,
             'vertexes': [{'VID': v.VID,
                           'name': v.name,
                           'description': v.description} for v in g.vertex_set.all()],
             'edges': [{'source': e.source.VID,
                        'target': e.target.VID,
                        'description': e.description} for e in Edge.objects.filter(source__graph=g)]}
        g_json = json.dumps(d, ensure_ascii=False)
        context['graph_json'] = g_json
        return context


class GraphFromJSONView(FormView):
    form_class = GraphFromJSONForm
    template_name = "graph/graph_from_JSON.html"

    def form_valid(self, form):
        g_dict = json.loads(form.cleaned_data['text'])
        if Graph.objects.filter(name=g_dict['name']).exists():
            raise Http404("Graph with this name already exists!")
        try:
            g = Graph.objects.create(name=g_dict['name'], description=g_dict['description'])
            self.pk = g.pk
            for v_dict in g_dict['vertexes']:
                Vertex.objects.create(graph=g,
                                      VID=v_dict['VID'],
                                      name=v_dict['name'],
                                      description=v_dict['description'])
            for e_dict in g_dict['edges']:
                Edge.objects.create(source=Vertex.objects.get(graph=g, VID=e_dict['source']),
                                    target=Vertex.objects.get(graph=g, VID=e_dict['target']),
                                    description=e_dict['description'])
        except Exception:
            raise Http404("Can't make graph")
        return super(GraphFromJSONView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('detail_graph', kwargs={'pk': self.pk})


class TopSortView(FormView):
    form_class = TopSortForm
    template_name = "graph/graph_topsort.html"

    def form_valid(self, form):
        if Graph.objects.filter(name=form.cleaned_data['new_name']).exists():
            raise Http404("Graph with this name already exists!")

        old_g = Graph.objects.get(pk=self.kwargs['pk'])
        new_g = Graph.objects.create(name=form.cleaned_data['new_name'],
                                     description=old_g.description)
        edges = Edge.objects.filter(source__graph=old_g)
        d = {}
        for vertex in old_g.vertex_set.all():
            d[vertex.VID] = [edge.target.VID for edge in vertex.outcoming_edges.all()]
        old_nxg = nx.DiGraph()
        old_nxg.add_nodes_from(d.keys())
        for k, v in d.items():
            old_nxg.add_edges_from(([(k, t) for t in v]))

        topsort_list = list(topological_sort(old_nxg))
        for i, old_VID in enumerate(topsort_list):
            Vertex.objects.create(graph=new_g,
                                  VID=i + 1,
                                  name=old_g.vertex_set.get(VID=old_VID).name,
                                  description=old_g.vertex_set.get(VID=old_VID).description)
        for edge in edges:
            old_source_VID = edge.source.VID
            old_target_VID = edge.target.VID
            new_source_VID = topsort_list.index(old_source_VID) + 1
            new_target_VID = topsort_list.index(old_target_VID) + 1
            new_source = new_g.vertex_set.get(VID=new_source_VID)
            new_target = new_g.vertex_set.get(VID=new_target_VID)
            Edge.objects.create(source=new_source,
                                target=new_target,
                                description=edge.description)
        self.pk = new_g.pk

        return super(TopSortView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('detail_graph', kwargs={'pk': self.pk})


class AddNullPointView(RedirectView):
    pattern_name = 'detail_graph'

    def get_redirect_url(self, *args, **kwargs):
        graph = get_object_or_404(Graph, pk=kwargs['pk'])
        null_point = Vertex.objects.create(graph=graph,
                                           VID=max(Vertex.objects.filter(graph=graph).values_list('VID', flat=True),
                                                   default=0) + 1,
                                           name="null-point")
        for v in graph.vertex_set.all().annotate(in_count=Count('incoming_edges')).filter(in_count=0):
            Edge.objects.create(source=null_point, target=v)
        return super().get_redirect_url(*args, **kwargs)
