import logging
import sys

from hyo2.qc.cli.cli import cli

logger = logging.getLogger(__name__)

logger.debug("initial argv: %s" % sys.argv)
sys.argv.append("FlierFinder")
sys.argv.append("--help")
logger.debug("passed argv: %s" % sys.argv)

cli()
