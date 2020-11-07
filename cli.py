# -*- coding: utf-8 -*-
import click

from sql_simulation.controller import Controller


@click.command(help='TiDB SQL 乱序测试工具')
@click.argument('file', nargs=-1, type=click.Path(exists=True))
@click.option('-o', '--output', help='输出结果文件')
def cli(file, output):
    if len(file) < 2:
        click.echo('输入的文件数必须大于 2 个')
        return

    controller = Controller(output=output)
    for f in file:
        controller.add_file(f)
    controller.run()


if __name__ == '__main__':
    cli()
