# -*- coding: utf-8 -*-
from sql_simulation.logger import logger


class Statement(object):
    def __init__(self, label, session, statement):
        self.session = session
        self.value = statement
        self.label = label

    def execute(self):
        state_info = []
        state_info.append('[{}]-[{}]'.format(self.label, self.value))
        try:
            r = self.session.execute(self.value)
            if r and r.returns_rows:
                state_info.append(str(r.fetchall()))
        except Exception as e:
            state_info.append(str(e))
        return state_info

    def __repr__(self):
        return '<Statement ({})>'.format(self.label)


class StatementFactory(object):
    def __init__(self, factory):
        self.factory = factory

    def execute(self):
        factory_info = []
        factory_info.append('-' * 50)

        for statement in self.factory:
            assert isinstance(statement, Statement)
            factory_info.extend(statement.execute())
        return factory_info
