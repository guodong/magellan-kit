import json
from itertools import product

class Host:
    def __init__(self, id):
        self.id = id
        self.ports = {}


class Port:
    def __init__(self, id):
        self.id = id
        self.program = None

        # revert pointer to device
        self.device = None


class Switch:
    def __init__(self, id):
        self.id = id
        self.ports = {}


class Topology:
    def __init__(self, topo_json):
        self.hosts = {}
        self.switches = {}
        self.links = []
        self.port_graph = []

        topo_obj = json.loads(topo_json)
        for id, ports in topo_obj['hosts'].items():
            h = Host(id)
            for pid, pconf in ports.items():
                p = Port(pid)
                p.device = h
                h.ports[pid] = p
            self.hosts[id] = h

        for id, ports in topo_obj['switches'].items():
            s = Switch(id)
            for pid, pconf in ports.items():
                p = Port(pid)
                p.device = s
                s.ports[pid] = p
            self.switches[id] = s

        for link in topo_obj['links']:
            src_dev_id, src_port_id = link[0].split(':', 1)  # TODO: check only have one ":"
            dst_dev_id, dst_port_id = link[1].split(':', 1)
            l = [{'device': self.__get_node_by_id(src_dev_id), 'port': self.__get_port_by_id(src_dev_id, src_port_id)},
                 {'device': self.__get_node_by_id(dst_dev_id), 'port': self.__get_port_by_id(dst_dev_id, dst_port_id)}]
            self.links.append(l)

            for s in self.switches.values():
                self.links += [[{'device': s, 'port': p1}, {'device': s, 'port': p2}] for p1, p2 in product(s.ports.values(), s.ports.values())]

    def __get_node_by_id(self, id):
        if id in self.hosts:
            return self.hosts[id]

        if id in self.switches:
            return self.switches[id]

        return None

    def __get_port_by_id(self, dev_id, port_id):
        dev = self.__get_node_by_id(dev_id)
        if dev is not None and port_id in dev.ports:
            return dev.ports[port_id]

        return None


