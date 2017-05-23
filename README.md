# FdwRosTest

Test-case for a bug that occurs when trying to read a ros bag file from within
a Multicorn Foreign Data Wrapper in PostgreSQL 9.6.

The same code runs fine outside PostgreSQL or in PostgreSQL 9.4 or 9.5!

## Install `python-rosbag`

```bash
$ sudo apt install python-rosbag
```

## Install Multicorn

```bash
$ git clone https://github.com/Kozea/Multicorn
$ cd Multicorn
$ make
$ sudo make install
```

## Install FdwRosTest

```bash
$ sudo pip install -e .
```

## Execute test outside PostgreSQL

```bash
$ python outsidepg.py
{'a': 'a 0', 'b': 'b 0'}
{'a': 'a 1', 'b': 'b 1'}
```

No crash. Things work as expected.

## Execute test inside PostgreSQL

Create database:

```bash
$ sudo -u postgres createdb fdwrostest
```

Copy bag file to `/tmp`:

```bash
$ cp test.bag /tmp
```

Stop the `postgresql` service:

```bash
$ sudo systemctl stop postgresql
```

Start a `postgresql` process in `single` mode under `gdb`, and execute the test
case:

```bash
$ sudo -u postgres gdb --args /usr/lib/postgresql/9.6/bin/postgres --single -D /var/lib/postgresql/9.6/main -c config_file=/etc/postgresql/9.6/main/postgresql.conf fdwrostest
…
(gdb) run
…
backend> create extension multicorn
backend> create server ros foreign data wrapper multicorn options (wrapper 'fdwrostest.FdwRosTest', bagfile '/tmp/test.bag')
backend> create foreign table ros (status smallint) server ros
backend> select * from ros;

Program received signal SIGSEGV, Segmentation fault.
__memmove_avx_unaligned_erms () at
../sysdeps/x86_64/multiarch/memmove-vec-unaligned-erms.S:364
364     ../sysdeps/x86_64/multiarch/memmove-vec-unaligned-erms.S: No such file or directory.
```

This is the full backtrace:

```
(gdb) bt
#0  __memmove_avx_unaligned_erms () at ../sysdeps/x86_64/multiarch/memmove-vec-unaligned-erms.S:364
#1  0x00007ffff1d7c40d in memcpy (__len=<optimized out>, __src=0x555557d473f4, __dest=<optimized out>) at /usr/include/x86_64-linux-gnu/bits/string3.h:53
#2  XXH_memcpy (size=<optimized out>, src=0x555557d473f4, dest=<optimized out>) at xxhash.c:95
#3  XXH32_update_endian (endian=XXH_littleEndian, len=<optimized out>, input=0x555557d473f4, state_in=0x555557afab80) at xxhash.c:589
#4  XXH32_update (state_in=0x555557afab80, input=0x555557d473f4, len=<optimized out>) at xxhash.c:662
#5  0x00007fffe40cef66 in decompressBlock () from /lib/x86_64-linux-gnu/libroslz4.so.1d
#6  0x00007fffe40cf089 in roslz4_decompress () from /lib/x86_64-linux-gnu/libroslz4.so.1d
#7  0x00007fffe42d323c in ?? () from /usr/lib/python2.7/dist-packages/roslz4/_roslz4.x86_64-linux-gnu.so
#8  0x00007fffe6006091 in PyEval_EvalFrameEx () from /lib/x86_64-linux-gnu/libpython2.7.so.1.0
#9  0x00007fffe6004390 in PyEval_EvalFrameEx () from /lib/x86_64-linux-gnu/libpython2.7.so.1.0
#10 0x00007fffe616d15c in PyEval_EvalCodeEx () from /lib/x86_64-linux-gnu/libpython2.7.so.1.0
#11 0x00007fffe600425d in PyEval_EvalFrameEx () from /lib/x86_64-linux-gnu/libpython2.7.so.1.0
#12 0x00007fffe60ce211 in ?? () from /lib/x86_64-linux-gnu/libpython2.7.so.1.0
#13 0x00007fffe600711d in ?? () from /lib/x86_64-linux-gnu/libpython2.7.so.1.0
#14 0x00007fffe6006091 in PyEval_EvalFrameEx () from /lib/x86_64-linux-gnu/libpython2.7.so.1.0
#15 0x00007fffe616d15c in PyEval_EvalCodeEx () from /lib/x86_64-linux-gnu/libpython2.7.so.1.0
#16 0x00007fffe60c15b0 in ?? () from /lib/x86_64-linux-gnu/libpython2.7.so.1.0
#17 0x00007fffe6059543 in PyObject_Call () from /lib/x86_64-linux-gnu/libpython2.7.so.1.0
#18 0x00007fffe6116cbc in ?? () from /lib/x86_64-linux-gnu/libpython2.7.so.1.0
#19 0x00007fffe6059543 in PyObject_Call () from /lib/x86_64-linux-gnu/libpython2.7.so.1.0
#20 0x00007fffe60ddcc2 in ?? () from /lib/x86_64-linux-gnu/libpython2.7.so.1.0
#21 0x00007fffe606424e in ?? () from /lib/x86_64-linux-gnu/libpython2.7.so.1.0
#22 0x00007fffe6059543 in PyObject_Call () from /lib/x86_64-linux-gnu/libpython2.7.so.1.0
#23 0x00007fffe605a995 in PyObject_CallFunction () from /lib/x86_64-linux-gnu/libpython2.7.so.1.0
#24 0x00007fffe651aa1b in getCacheEntry (foreigntableid=<optimized out>, foreigntableid@entry=1383341) at src/python.c:627
#25 0x00007fffe651ac99 in getInstance (foreigntableid=foreigntableid@entry=1383341) at src/python.c:673
#26 0x00007fffe651f13e in multicornGetForeignRelSize (root=0x555555fb3b18, baserel=0x5555560aee68, foreigntableid=1383341) at src/multicorn.c:237
#27 0x0000555555805372 in ?? ()
#28 0x000055555580645e in make_one_rel ()
#29 0x0000555555824f3c in query_planner ()
#30 0x0000555555826fa5 in ?? ()
#31 0x0000555555829ddc in subquery_planner ()
#32 0x000055555582ad6e in standard_planner ()
#33 0x00005555558cc76b in pg_plan_query ()
#34 0x00005555558cc871 in pg_plan_queries ()
#35 0x00005555558ce56a in PostgresMain ()
#36 0x00005555555fb639 in main ()
```
