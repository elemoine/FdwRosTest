import sys
from multicorn import ForeignDataWrapper

sys.argv = []  # hack for rosbag

from rosbag import Bag


class FdwRosTest(ForeignDataWrapper):
    def __init__(self, options, columns=None):
        super(FdwRosTest, self).__init__(options, columns)
        self.columns = columns

        bag = Bag(options.get('bagfile'), 'r')
        it = bag.read_messages()

        # attempt to read from the ros bag file
        next(it)  # -> crash!

    def execute(self, quals, columns):
        for i in range(0, 2):
            line = {}
            for column in self.columns:
                line[column] = '%s %s' % (column, i)
            yield line

