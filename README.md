# SQL 乱序模拟

## 目的

模拟多个客户端乱序向 TiDB 执行 SQL 语句。

以两个客户端的情况为例。首先启动两个 TiDB 客户端，客户端分别读取对应的 SQL 文件后，以交错顺序执行 SQL 文件中的语句。要求穷举所有执行顺序。

给定 sql1.txt、sql2.txt, 内容如下：

```
# cat sql1.txt
update X set a=5 where id=1;
update X set a=6 where id=2;
```

```
# cat sql2.txt
update X set a=8 where id=8
```

启动客户端 client1 读取 sql1.txt、client2 读取 sql2.txt。

对这个 case，穷举所有可能，意味着执行顺序必须包含以下三种情况：

情况 1：

```
client1：update X set a=5 where id=1;
client1：update X set a=6 where id=2;
client2：update X set a=8 where id=8;
```

情况 2：

```
client1：update X set a=5 where id=1;
client2：update X set a=8 where id=8;
client1：update X set a=6 where id=2;
```

情况 3：

```
client2：update X set a=8 where id=8;
client1：update X set a=5 where id=1;
client1：update X set a=6 where id=2;
```

## 模拟结果

见 examples 里两个例子。

`output_optimistic.txt` 是乐观锁下的模拟过程。

`output_pessimistic.txt` 是悲观锁下的模拟过程。


## 使用

```
pipenv --python 3
pipenv install

# 准备数据库及初始的表
# 更改 .env 文件，配置 TiDB 地址
# 准备多个 SQL 脚本

pipenv run python cli.py data/script_a.txt data/script_b.txt -o output.log

# 执行过程及结果，在输出的 output.log 里

# 测试代码
pipenv run pytest --cov sql_simulation tests

```

## 注意事项

* 因为是所有组合全排列，如果 SQL 文件过多或语句比较多时，会比较慢。
* 一个 SQL 文件用一个 session，为了方便查看，记录中标记了文件名来区分不同的 session。
* 悲观锁下，如果产生了行锁，导致执行时间较长，建议设置超时时间为较短的值。如：`set @@innodb_lock_wait_timeout=2;`
* 为了方便查看结果，如果是 select 语句，会打印输出，如果有 error 也会打印输出。
* 简单处理，一行记录是一个 statement，如果 'update t2 set id=id+1;select * from t2' 这种语句，没有 select 的输出。

## TiDB 事务简单说明

### 悲观锁

* 悲观锁下，事务 B 的 update 时，如果有其他事务抢占了行锁，且未提交事务释放锁，会等待，默认时间为 50秒。
* 如果事务 B 的 update，在其他事务抢占行锁，提前释放行锁后，可以提交成功。

例子：

```
# 未提交时，update 会等待超时
[script_b.txt]-[start transaction;]
[script_b.txt]-[select * from t1;]
[(2658,)]
[script_a.txt]-[start transaction;]
[script_b.txt]-[update t1 set id=id+1;]
[script_a.txt]-[select * from t1;]
[(2658,)]
[script_a.txt]-[update t1 set id=id+1;]
(pymysql.err.OperationalError) (1205, 'Lock wait timeout exceeded; try restarting transaction')
[SQL: update t1 set id=id+1;]
(Background on this error at: http://sqlalche.me/e/13/e3q8)
[script_b.txt]-[commit;]
[script_a.txt]-[commit;]

```

```
# commit b 后， a 在 update，不会报错，结果为 2662
[script_b.txt]-[start transaction;]
[script_b.txt]-[select * from t1;]
[(2660,)]
[script_a.txt]-[start transaction;]
[script_a.txt]-[select * from t1;]
[(2660,)]
[script_b.txt]-[update t1 set id=id+1;]
[script_b.txt]-[commit;]
[script_a.txt]-[update t1 set id=id+1;]
[script_a.txt]-[commit;]
```

```
[script_b.txt]-[start transaction;]
[script_a.txt]-[start transaction;]
[script_a.txt]-[select * from t1;]
[(159,)]
[script_b.txt]-[select * from t1;]
[(159,)]
[script_a.txt]-[update t1 set id=id+1;]
[script_a.txt]-[commit;]
[script_b.txt]-[update t1 set id=id+1;]
[script_a.txt]-[update t1 set id=id+1;]
(pymysql.err.OperationalError) (1205, 'Lock wait timeout exceeded; try restarting transaction')
[SQL: update t1 set id=id+1;]
(Background on this error at: http://sqlalche.me/e/13/e3q8)
[script_b.txt]-[commit;]

```

### 乐观锁

* 如果两个事务同时对一行数据操作，操作时不会报错，当 commit 时会比较版本，后提交的会失败。

例子：

```
[script_b.txt]-[start transaction;]
[script_b.txt]-[select * from t1;]
[(2892,)]
[script_b.txt]-[update t1 set id=id+1;]
[script_a.txt]-[start transaction;]
[script_b.txt]-[commit;]
[script_a.txt]-[select * from t1;]
[(2892,)]
[script_a.txt]-[update t1 set id=id+1;]
[script_a.txt]-[commit;]
(pymysql.err.OperationalError) (9007, 'Write conflict, txnStartTS=420670725395316742, conflictStartTS=420670725395316738, conflictCommitTS=420670725395316743, key={tableID=71, handle=1} primary={tableID=71, handle=1} [try again later]')
[SQL: commit;]
(Background on this error at: http://sqlalche.me/e/13/e3q8)

```

