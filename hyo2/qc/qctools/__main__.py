import logging

from hyo2.qc.qctools import gui

logger = logging.getLogger()


def set_logging(default_logging=logging.WARNING, hyo2_logging=logging.INFO, abc_logging=logging.DEBUG):
    logging.basicConfig(
        level=default_logging,
        format="%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s"
    )
    logging.getLogger("hyo2").setLevel(hyo2_logging)
    logging.getLogger("hyo2.qc").setLevel(abc_logging)
    logging.getLogger("hyo2.rori").setLevel(abc_logging)
    logging.getLogger("hyo2.unccalc").setLevel(abc_logging)


set_logging()

gui.gui()
