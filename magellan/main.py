import inspect
from .flow_program import FlowProgram
import ast, astunparse
from .node_visitor import NodeVisitor
from .data_store import DataStore
from globals import functions
from parser import defaultParser

ds = DataStore()

programs = {}
switches = []



def func(udf):
    functions[udf.__name__] = udf


# TODO: parallel compile each program
def magellan(label='default', parser=defaultParser):
    programs[label] = {}

    def f(func):
        source = inspect.getsource(func)
        programs[label]['source'] = source
        fp = gen_flow_program(source)
        fp.gen_pit_pipeline()
        fp.dump_pit()
        # programs[lab]['fp'] = fp

    return f


def gen_flow_program(source):
    root = ast.parse(source)
    # print(astunparse.dump(root))
    fp = FlowProgram(ds.get_all())
    visitor = NodeVisitor(fp)
    visitor.visit(root)
    fp.dump()
    return fp
