from hyo2.qc.common.helper import Helper
from hyo2.qc.common import testing

from collections import defaultdict

d0 = {}
print("d0: %d" % Helper.total_size(d0))

d1 = {1: 0.0}
print("d1: %d" % Helper.total_size(d1))

d2 = defaultdict(int)
d2[1] = 0.0
print("d2: %d" % Helper.total_size(d2))


