import networkx as nx
from magellan import magellan, ds, helper, topo, assign_label, func, defaultParser, topology


@assign_label
def assign(port):
    if isinstance(port.peer().device, topology.Host):
        return 'external_ingress'


@func
def shortest_path(src, dst):
    G = nx.Graph()
    for e in topo.links:
        G.add_edge(e[0]['device'].id + ':' + e[0]['port'].id, e[1]['device'].id + ':' + e[1]['port'].id)

    path = nx.shortest_path(G, source=src, target=dst)
    return helper.to_standard_path(path)


@func
def spanning_tree():
    G = nx.Graph()
    for e in topo.links:
        G.add_edge(e[0]['device'].id + ':' + e[0]['port'].id, e[1]['device'].id + ':' + e[1]['port'].id)
    tree = nx.minimum_spanning_tree(G)
    return helper.to_standard_tree(tree.edges(data=True))


ds.init({
    'host_table': 'map'
})


@magellan(label='external_ingress', parser=defaultParser)
def on_packet(pkt, ingress):
    host_table[pkt.eth.src] = ingress

    if pkt.eth.dst in host_table:
        move(pkt, shortest_path(ingress, host_table[pkt.eth.dst]))
    else:
        move(pkt, spanning_tree())




