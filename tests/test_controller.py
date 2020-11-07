# -*- coding: utf-8 -*-
from pathlib import Path

from sql_simulation.controller import Controller


def test_demo():
    c = Controller()
    data_folder = str((Path(__file__).parent / 'data').absolute())
    c.add_file('{}/{}'.format(data_folder, 'demo_a.txt'))
    c.add_file('{}/{}'.format(data_folder, 'demo_b.txt'))
    c.run()
