import logging

logger = logging.getLogger(__name__)

from hyo2.grids._grids import ProgressCallback


class QtGridCallback(ProgressCallback):

    def __init__(self, progress=None):
        super().__init__()
        self.progress = progress

    def update(self, n, tot):

        if self.progress is None:

            if tot <= 10:
                return
            if tot <= 100:
                quantum = int(tot / 10)
            else:
                quantum = int(tot / 100)
            if (n % quantum) == 0:
                print("[CLI] -> %.2f" % ((n / tot) * 100))

        else:

            try:
                self.progress.update((n / tot) * 100, restart=True)
            except Exception as e:
                print(e)

    # noinspection PyMethodOverriding
    def step_update(self, text, n, tot):

        if self.progress is None:
            if tot <= 10:
                return
            if tot <= 100:
                quantum = int(tot / 10)
            else:
                quantum = int(tot / 100)
            if (n % quantum) == 0:
                print("[CLI] -> %.2f [%s]" % ((n / tot) * 100, text))

        else:

            try:
                self.progress.update((n / tot) * 100, text=text, restart=True)
            except Exception as e:
                print(e)
