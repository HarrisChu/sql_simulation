# -*- coding: utf-8 -*-
import pytest

from sql_simulation.controller import Controller


@pytest.fixture(scope='session')
def db():
    c = Controller()
    c.engine.execute('create table `t2` (`id` int(11) default null)')
    c.engine.execute('insert into `t2` values (1)')
    yield

    c.engine.execute('drop table t2;')
