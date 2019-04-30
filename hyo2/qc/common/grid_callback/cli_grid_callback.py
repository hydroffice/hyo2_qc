import logging

from hyo2.grids._grids import ProgressCallback

logger = logging.getLogger(__name__)


class CliGridCallback(ProgressCallback):

    def __init__(self):
        super().__init__()

    # noinspection PyMethodOverriding
    def step_update(self, text, n, tot):

        if tot <= 10:
            return
        if tot <= 100:
            quantum = int(tot / 10)
        else:
            quantum = int(tot / 100)
        if (n % quantum) == 0:
            print("[CLI] -> %.2f [%s]" % ((n / tot) * 100, text))
