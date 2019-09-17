from __future__ import print_function

import sys, os, inspect, importlib
from .table import Table
from .variable import RefVariable, ConstantVariable, TupleVariable
from globals import functions

NONSENSE = "None"
MATCHANY = "*"
PRIORITY = "pri"
DATA = "data"
TRUE = "True"
FALSE = "False"


class Instruction:
    def __init__(self, gv, inputs, outputs, mapping):
        self.gv = gv
        self.inputs = inputs
        self.outputs = outputs
        self.mapping = mapping
        self.pit = Table()

    def gen_pit(self):

        for output in self.outputs:
            self.pit.schema.outputs.append(output.name)

        if self.gv is not None:
            self.pit.schema.inputs.append(self.gv.name)
        if self.mapping == 'in':
            self.pit.schema.inputs.append(self.inputs[0].name)
        elif self.mapping != 'assignmap' and self.mapping != 'varof':
            for input in self.inputs:
                self.pit.schema.inputs.append(input.name)

        if self.mapping == 'varof':
            self.pit.schema.inputs.append(self.inputs[1].name)
            self.outputs[0].value = []
            for (k, v) in self.inputs[0].value.items():
                entry = {PRIORITY: 1,
                         DATA: {
                             self.inputs[1].name: k,
                             self.outputs[0].name: v}
                         }
                if self.gv is not None:
                    entry[DATA].update({self.gv.name: TRUE})
                self.pit.entries.append(entry)
                self.outputs[0].value.append(v)

            entry2 = {PRIORITY: 0,
                      DATA: {
                          self.inputs[1].name: MATCHANY,
                          self.outputs[0].name: NONSENSE}
                      }
            if self.gv is not None:
                entry2[DATA].update({self.gv.name: MATCHANY})
            self.pit.entries.append(entry2)
        elif self.mapping == 'in':
            v = self.inputs[1]
            if isinstance(self.inputs[1], RefVariable):
                v = self.inputs[1].dst
            for val in v.value.keys():
                entry = {
                    PRIORITY: 1,
                    DATA: {
                        self.inputs[0].name: val,
                        self.outputs[0].name: TRUE
                    }
                }
                if self.gv is not None:
                    entry[DATA].update({self.gv.name: TRUE})
                self.pit.entries.append(entry)
            entry = {
                PRIORITY: 0,
                DATA: {
                    self.inputs[0].name: MATCHANY,
                    self.outputs[0].name: FALSE
                }
            }
            if self.gv is not None:
                entry[DATA].update({self.gv.name: TRUE})
            self.pit.entries.append(entry)
        elif self.mapping == 'assign':  # input can't be map
            # TODO: current code only handles map
            for i in self.inputs[0].value:
                entry = {
                    PRIORITY: 1,
                    DATA: {
                        self.inputs[0].name: i,
                        self.outputs[0].name: i
                    }
                }
                if self.gv is not None:
                    entry[DATA].update({self.gv.name: TRUE})
                self.pit.entries.append(entry)
        elif self.mapping == 'assignmap':
            self.pit.schema.inputs.append(self.inputs[1].name)
            self.pit.schema.inputs.append(self.inputs[2].name)
            self.pit.schema.outputs.append('action')
            for k, v in self.inputs[0].value.items():
                entry = {
                    PRIORITY: 1,
                    DATA: {
                        self.inputs[1].name: k,
                        self.inputs[2].name: v,
                        'action': 'nop'
                    }
                }
                self.pit.entries.append(entry)
            self.pit.entries.append({
                PRIORITY: 0,
                DATA: {
                    self.inputs[1].name: MATCHANY,
                    self.inputs[2].name: MATCHANY,
                    'action': 'toController'

                }
            })
        elif self.mapping == 'not':

            self.pit.entries.append({
                PRIORITY:1,
                DATA:{
                # self.gv.name:TRUE,
                self.inputs[0].name: TRUE,
                self.outputs[0].name: FALSE}
            })
            self.pit.entries.append({
                PRIORITY:1,
                DATA:{
                # self.gv.name:TRUE,
                self.inputs[0].name: FALSE,
                self.outputs[0].name: TRUE}
            })
        else: # udf
            if self.mapping not in ['move', 'spanning_tree']:
                functions[self.mapping]('s1', 's2')

    def dump(self):
        if self.gv is not None:
            if len(self.outputs) == 0:
                print('if %s: %s(%s)' % (self.gv.name, self.mapping,
                                         ', '.join(map(lambda s: s.dump(), self.inputs))))
            else:
                print('if %s: %s = %s(%s)' % (
                    self.gv.name, ', '.join(map(lambda s: s.dump(), self.outputs)), self.mapping,
                    ', '.join(map(lambda s: s.dump(), self.inputs))))
        else:
            if len(self.outputs) == 0:
                print('%s(%s)' % (self.mapping,
                                  ', '.join(map(lambda s: s.dump(), self.inputs))))
            else:
                print('%s = %s(%s)' % (', '.join(map(lambda s: s.dump(), self.outputs)), self.mapping,
                                       ', '.join(map(lambda s: s.dump(), self.inputs))))
        # s1 = ' '.join(map(lambda s: astunparse.unparse(s), self.outputs))
        # print '%s = func(%s)' % (s1, ' '.join(map(lambda s: astunparse.unparse(s), self.inputs)))
        # print '%s = assign(%s)' % (' '.join(map(lambda s: s.id, self.outputs)), ' '.join(map(lambda s: s.n, self.inputs)))

    def dump_pit(self):
        # if self.mapping == 'valof':

        # gv = ''
        # if self.gv is not None:
        #     gv = self.gv.name
        #     print '%s | %s -> %s' % (gv, '|'.join(self.pit.schema.inputs), '|'.join(self.pit.schema.outputs))
        # else:
        if not (self.pit is None):
            print(PRIORITY, end='|')
            print('%s -> %s' % ('|'.join(self.pit.schema.inputs), '|'.join(self.pit.schema.outputs)))
            for entry in self.pit.entries:
                print(entry[PRIORITY], end='|')
                for input_name in self.pit.schema.inputs:
                    print(entry[DATA][input_name], end='|')
                for output_name in self.pit.schema.outputs:
                    print(entry[DATA][output_name])

    '''
    def dump_pit(self):
        # if self.mapping == 'valof':

        # gv = ''
        # if self.gv is not None:
        #     gv = self.gv.name
        #     print '%s | %s -> %s' % (gv, '|'.join(self.pit.schema.inputs), '|'.join(self.pit.schema.outputs))
        # else:
        print('%s -> %s' % ('|'.join(self.pit.schema.inputs), '|'.join(self.pit.schema.outputs)))


        for entry in self.pit.entries:
            for input_name in self.pit.schema.inputs:
                print(entry[input_name] + '|',)
            for output_name in self.pit.schema.outputs:
                if isinstance(entry[output_name], list):
                    print(entry[output_name])
                else:
                    print(entry[output_name])
    '''
