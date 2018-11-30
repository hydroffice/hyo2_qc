import logging

logger = logging.getLogger(__name__)

from hyo2.grids._grids import ProgressCallback


class CliGridCallback(ProgressCallback):

    def update(self, n, tot):

        quantum = int(tot / 100)
        if (n % quantum) == 0:
            print("[CLI] -> %s / %s" % (n, tot))
            print("[CLI] -> %.2f" % ((n / tot) * 100,))

    # noinspection PyMethodOverriding
    def step_update(self, text, n, tot):

        quantum = int(tot / 100)
        if (n % quantum) == 0:
            print("[CLI] -> %.2f [%s]" % ((n / tot) * 100, text))
