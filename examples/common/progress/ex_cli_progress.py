import time

from hyo2.abc.lib.logging import set_logging
import logging

from hyo2.qc.common.progress.cli_progress import CliProgress

logger = logging.getLogger(__name__)
set_logging(ns_list=["hyo2.qc", ])

progress = CliProgress()

progress.start(title='Test Bar', text='Doing stuff', min_value=100, max_value=300, init_value=100)

time.sleep(1.)

progress.update(value=135, text='Updating')

time.sleep(1.)

progress.add(quantum=33, text='Updating')

time.sleep(1.)

print("canceled? %s" % progress.canceled)

progress.end()

