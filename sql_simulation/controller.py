# -*- coding: utf-8 -*-
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import OperationalError

from sql_simulation.statement import StatementFactory, Statement
from sql_simulation.utils import Generator
from sql_simulation.config import Config
from sql_simulation.logger import logger


class Controller(object):
    def __init__(self, parse_class=None, output=None):
        if output is None:
            output = 'output.log'
        self.output = output
        self.statement_factories = []
        self.parse_class = parse_class or Parser
        uri = '{user}:{password}@{host}:{port}/{db}'.format(user=Config.TIDB_USER,
                                                            password=Config.TIDB_PASSWORD,
                                                            host=Config.TIDB_HOST,
                                                            port=Config.TIDB_PORT,
                                                            db=Config.TIDB_DATABASE)

        self.engine = create_engine('mysql+pymysql://{}?charset=utf8'.format(uri), pool_size=1, pool_timeout=10)
        try:
            self.engine.execute('show tables;')
        except OperationalError as e:
            raise e

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
        length = len(result_list)
        with open(self.output, 'w') as fl:
            fl.write('共有 {} 种组合'.format(length))
            logger.info('共有 {} 种组合'.format(length))
            fl.write('\n')

            index = 0
            for result in result_list:
                index += 1
                fl.write('-' * 20 + '第{}/{}个组合'.format(index, length) + '-' * 20)
                fl.write('\n')
                statement_factory = StatementFactory(result)
                factory_info = statement_factory.execute()
                fl.write('\n'.join(factory_info))
                fl.write('\n')
                if index % 10 == 0:
                    logger.info('执行到第{}个组合'.format(index))
                    fl.flush()
                # 防止上个组合有未提交，占锁的情况
                for session in self.session_list:
                    try:
                        session.commit()
                    except:
                        session.rollback()


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
