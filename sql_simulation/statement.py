# -*- coding: utf-8 -*-
from sql_simulation.logger import logger


class Statement(object):
    def __init__(self, label, session, statement):
        self.session = session
        self.value = statement
        self.label = label

    def execute(self):
        logger.info('[execute]-[{}]-[{}]'.format(self.label, self.value))
        try:
            r = self.session.execute(self.value)
            if r and r.returns_rows:
                logger.info(r.fetchall())
        except Exception as e:
            logger.info(e)

    def __repr__(self):
        return '<Statement ({})>'.format(self.label)


class StatementFactory(object):
    def __init__(self, factory):
        self.factory = factory

    def execute(self):
        logger.info('-' * 50)

        for statement in self.factory:
            assert isinstance(statement, Statement)
            statement.execute()
