from fdwrostest import FdwRosTest


if __name__ == '__main__':
    options = {'bagfile': 'test.bag'}
    columns = {'a': 'a', 'b': 'b'}

    # no crash when run outside PostgreSQL
    fdw = FdwRosTest(options, columns)

    for line in fdw.execute(None, None):
        print(line)

