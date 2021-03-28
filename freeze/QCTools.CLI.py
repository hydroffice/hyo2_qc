import logging

from hyo2.abc.lib.logging import set_logging
from hyo2.qc.cli.cli import cli

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

cli()
