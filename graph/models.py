from django.db import models
from django.forms import ModelForm, CharField, Textarea
import networkx as nx
from django.apps import apps
import matplotlib.pyplot as plt
from django.core.files.base import ContentFile
from io import BytesIO
from django.db.models.signals import post_save
from django.dispatch import receiver
from networkx.drawing.nx_agraph import graphviz_layout

class Graph(models.Model):
    name = models.CharField(max_length = 128, unique = True)
    description = models.TextField(null = True, blank = True)
    image = models.ImageField(upload_to='graphs/', null = True, default = None)
    
    def __str__(self):
        return self.name
    
    def create_image(self):
        Edge = apps.get_model(app_label='graph', model_name='Edge')
        edges = Edge.objects.filter(source__graph = self)
        d = {}
        for vertex in self.vertex_set.all():
            d[vertex.VID] = [edge.target.VID for edge in vertex.outcoming_edges.all()]
        g = nx.DiGraph()
        g.add_nodes_from(d.keys())
        for k, v in d.items():
            g.add_edges_from(([(k, t) for t in v]))
        #pos = graphviz_layout(g)
        nx.draw_kamada_kawai(g, with_labels=True)
        f = BytesIO()
        plt.savefig(f)
        content_file = ContentFile(f.getvalue())
        self.image.delete()
        self.image.save(self.name+".png", content_file)
        plt.figure()

class Vertex(models.Model):
    class Meta:
        ordering = ['VID']
        
    graph = models.ForeignKey(Graph, on_delete = models.CASCADE)
    VID = models.IntegerField(null = False)
    name = models.CharField(max_length = 128, null = False)
    description = models.TextField(null = True, blank = True)
    
    def __str__(self):
        return str(self.graph) + ': ' + str(self.VID) + ', ' + str(self.name)
    
class Edge(models.Model):
    class Meta:
        ordering = ['source__VID', 'target__VID']
    source = models.ForeignKey(Vertex, on_delete = models.CASCADE, related_name = 'outcoming_edges')
    target = models.ForeignKey(Vertex, on_delete = models.CASCADE, related_name = 'incoming_edges')
    description = models.TextField(null = True, blank = True)

class AddEdgeForm(ModelForm):
    class Meta:
        model = Edge
        fields = ['source', 'target', 'description']

    def __init__(self, pk, *args, **kwargs):
        super(AddEdgeForm, self).__init__(*args, **kwargs)
        self.fields['source'].queryset = Vertex.objects.filter(graph__pk = pk)
        self.fields['target'].queryset = Vertex.objects.filter(graph__pk = pk)

class AddEdgeVertexForm(ModelForm):
    class Meta:
        model = Vertex
        fields = ['graph', 'VID', 'name', 'description']
    edge_description = CharField(label = 'Edge description', widget=Textarea, required=False)

@receiver(post_save, sender=Vertex)
@receiver(post_save, sender=Edge)
def my_handler(sender, instance, **kwargs):
    graph = instance.graph if sender is Vertex else instance.source.graph
    if graph.image:
        graph.image.delete()
    graph.create_image()
