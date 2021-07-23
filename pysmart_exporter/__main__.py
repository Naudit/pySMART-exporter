# Copyright (C) 2021 Rafael Leira
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# License for more details.
#
################################################################
"""The pysmart_exporter main file
"""

import prometheus_client
from pysmart_exporter.collector import PySMARTCollector
import time
import sys

if __name__ == '__main__':
    collector = PySMARTCollector(prog='python3 -m pysmart_exporter')
    registry = prometheus_client.CollectorRegistry()
    registry.register(collector)
    args = collector.args

    if args['listen']:
        (ip, port) = args['listen'].split(':')
        prometheus_client.start_http_server(port=int(port),
                                            addr=ip, registry=registry)
        while True:
            time.sleep(3600)

    if args['textfile_name']:
        while True:
            collector.collect()
            prometheus_client.write_to_textfile(args['textfile_name'],
                                                registry)
            if collector.args['oneshot']:
                sys.exit(0)
            time.sleep(args.get('interval', 60))
