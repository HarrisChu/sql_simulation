# -*- coding: utf-8 -*-
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from sql_simulation.statement import StatementFactory, Statement
from sql_simulation.utils import Generator
from sql_simulation.logger import logger


class Controller(object):
    def __init__(self, parse_class=None):
        self.statement_factories = []
        self.parse_class = parse_class or Parser
        self.engine = create_engine('mysql+pymysql://root@192.168.90.67:4000/harris?charset=utf8', pool_size=1)
        self.generator = Generator()
        self.session_list = []

    def add_file(self, path):
        """
        一个脚本文件，使用同一个 SQL 的 session
        :param path:
        :return:
        """

        session = scoped_session(sessionmaker(bind=self.engine))
        self.session_list.append(session)
        self.generator.add_list(self.parse_class().parse(session, path))

    def run(self):
        result_list = self.generator.generate()
        logger.info('共有 {} 种组合'.format(len(result_list)))
        for result in result_list:
            statement_factory = StatementFactory(result)
            statement_factory.execute()
            # 防止上个组合有未提交，占锁的情况
            for session in self.session_list:
                session.commit()


class Parser(object):
    def parse(self, session, path):
        """
        解析文件，返回 statement 列表，简单处理，假定每一行是一个正常的语句，忽略注释。
        :param session:
        :param path:
        :return:
        """
        statements = []
        label = Path(path).name
        with open(path, 'r') as fl:
            for line in fl.readlines():
                line.replace('\n', '')
                line = line.strip()
                if line is not '':
                    statements.append(Statement(label, session, line))
        return statements
