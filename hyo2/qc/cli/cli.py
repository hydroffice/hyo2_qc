from hyo2.qc.cli.qctools_parser import QCToolsParser


def cli():
    prs = QCToolsParser()
    prs.run()


def parser():
    return QCToolsParser().parser

