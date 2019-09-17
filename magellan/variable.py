class Variable:
    def __init__(self, name):
        self.name = name
        self.value = []
        self.type = None
        self.ssa = []
        self.ssa_id = 0
        self.aliases = []

    def dump(self):
        if self.type == 'int':
            return '%s(%s)' % (self.name, str(self.value[0]))
        elif self.type == 'str':
            return '%s(\'%s\')' % (self.name, str(self.value[0]))
        else:
            return self.name


class RefVariable(Variable):
    def __init__(self, name, dst):
        Variable.__init__(self, name)
        self.type = 'ref'
        self.dst = dst


# a = 1
# a = assign(_v1)
class ConstantVariable(Variable):
    def __init__(self, name, value):
        Variable.__init__(self, name)
        self.value = [value]


class TupleVariable(Variable):
    def __init__(self, name, elts):
        Variable.__init__(self, name)
        self.elts = elts
