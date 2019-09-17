from main import magellan, func
from data_store import DataStore
from topology import Topology
import helper
from parser import defaultParser
import sys, json


def move(pkt, path):
    pass


ds = DataStore()

with open(sys.argv[1]) as f:
    topo = Topology(f.read())


def assign_label(func):
    # TODO: call assign label when got topo
    pass
