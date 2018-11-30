import logging


class SettingsFilter(logging.Filter):
    def filter(self, record):
        # print(record.name, record.levelname)
        if record.name.startswith('hyo2.qctools.settings') and (record.levelname == "INFO"):
            return False
        if record.name.startswith('matplotlib') and (record.levelname == "DEBUG"):
            return False
        return True


# logging settings
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # change to WARNING to reduce verbosity, DEBUG for high verbosity
ch_formatter = logging.Formatter('%(levelname)-9s %(name)s.%(funcName)s:%(lineno)d > %(message)s')
ch.setFormatter(ch_formatter)
ch.addFilter(SettingsFilter())
logger.addHandler(ch)


from hyo2.qc.qctools.gui import gui
gui()
