#!/usr/bin/env python
#
# Copyright (C) 2021 Rafael Leira
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# License for more details.
#
################################################################
"""Collect pysmart metrics,publish them via http or save them to a file.
This code is inspired on https://github.com/Showmax/prometheus-ethtool-exporter as base
"""

import argparse
import logging
import re
import sys
from typing import Union

from .version import __version__
from pySMART import DeviceList, Device
from pySMART.interface import NvmeAttributes
from prometheus_client.core import (
    GaugeMetricFamily,
    InfoMetricFamily,
    StateSetMetricFamily,
)


class PySMARTCollector(object):
    """Collect smartctl metrics using pySMART and publish them via http or save them to a file."""

    def __init__(self, args=None, prog=None):
        """Construct the PySMARTCollector object and parse the arguments."""
        self.args = None

        if not args:
            args = sys.argv[1:]

        self._parse_args(args, prog)

    def _parse_args(self, args, prog=None):
        """Parse CLI args and set them to self.args."""
        parser = argparse.ArgumentParser(prog=prog)
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '-f',
            '--textfile-name',
            dest='textfile_name',
            help=('Full file path where to store data for node collector to pick up'),
        )
        group.add_argument('-l', '--listen', dest='listen', help='Listen host:port, i.e. 0.0.0.0:9417')
        parser.add_argument(
            '-i',
            '--interval',
            dest='interval',
            type=int,
            default=60,
            help=('Number of seconds between updates of the textfile. Defaults 60 seconds.'),
        )
        parser.add_argument(
            '-1',
            '--oneshot',
            dest='oneshot',
            action='store_true',
            default=False,
            help='Run only once and exit. Useful for running in a cronjob',
        )
        parser.add_argument(
            '-q',
            '--quiet',
            dest='quiet',
            action='store_true',
            default=False,
            help='Silence any error messages and warnings',
        )
        parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
        arguments = parser.parse_args(args)
        if arguments.quiet:
            logging.getLogger().setLevel(100)
        if arguments.oneshot and not arguments.textfile_name:
            logging.error('Oneshot has to be used with textfile mode')
            parser.print_help()
            sys.exit(1)
        self.args = vars(arguments)

    def add_metric(
        self,
        gauges,
        disk: Device,
        name: str,
        value: Union[int, str] = 1,
        description: str = None,
        labels={},
        type='gauge',
    ):
        """Adds a metric to the gauges list

        Args:
            gauges (List): The list of metrics
            disk (Device): A disk object
            name (str): The name of the metric to be added
            value (Union[int, str], optional): The value of the metric. Defaults to 1.
            description (str, optional): A custom description for the metric. Defaults to None.
            labels (dict, optional): A custom dict of labels. Defaults to {}.
            type (str, optional): The metric type. Can be: 'info', 'state' or 'gauge'. Defaults to 'gauge'.
        """

        if 'device' not in labels:
            labels['device'] = disk.name

        # Fix labels
        if type == 'state':
            # raid_id must be present always in case there is at least 1 raid
            # This is a prometheus_cli lib limitation
            if 'raid_id' not in labels:
                labels['raid_id'] = 'N/A'

        # Add gauges
        if name not in gauges:
            if description is None:
                description = 'PySMART metric ' + name

            if type == 'info':
                gauges[name] = InfoMetricFamily('pysmart', description, labels=labels.keys())
            elif type == 'state':
                gauges[name] = StateSetMetricFamily('pysmart_' + name, description, labels=labels.keys())
            else:
                gauges[name] = GaugeMetricFamily('pysmart_' + name, description, labels=labels.keys())

        for k in labels.keys():
            if labels[k] is None:
                labels[k] = 'N/A'

        # Add values
        if type == 'info':
            gauges[name].add_metric(labels.values(), labels)
        elif type == 'state':
            gauges[name].add_metric(labels.values(), value)
        else:
            gauges[name].add_metric(labels.values(), value)

    def update_pysmart_stats(self, disk: Device, gauges):
        """Update gauge with statistics from pySmart."""

        # Common labels
        common_labels = {
            'device': disk.name,
            'interface': disk.smartctl_interface,
        }

        if 'megaraid,' in disk.smartctl_interface:
            try:
                common_labels['raid_id'] = re.match(r'.*megaraid,(\d+)', disk.smartctl_interface).groups()[0]
            except:
                pass

        # Check for raid

        # Info
        # All label values should be strings, even if they are None.
        # Force them all through the str() call
        info_labels = {
            'interface': str(disk.smartctl_interface),
            'model': str(disk.model),
            'rotation': str(disk.rotation_rate),
            'serial': str(disk.serial),
            'size_raw': str(disk.size_raw),
            'size': str(disk.size),
            'ssd': str(disk.is_ssd),
            'firmware': str(disk.firmware),
            'smart_capable': str(disk.smart_capable),
            'smart_enabled': str(disk.smart_enabled),
            'vendor': str(disk.vendor),
            'sector_size': str(disk.sector_size),
            'logical_sector_size': str(disk.logical_sector_size),
            'physical_sector_size': str(disk.physical_sector_size),
            **common_labels,
        }
        self.add_metric(gauges, disk, 'info', 1, labels=info_labels, type='info')

        # Assessment / Disk state
        if disk.assessment is not None:
            self.add_metric(
                gauges,
                disk,
                'assessment_passed',
                1 if disk.assessment == 'PASS' else 0,
                labels=common_labels,
            )

        # Temperature
        if disk.temperature is not None:
            self.add_metric(gauges, disk, 'temperature', disk.temperature, labels=common_labels)

        # Size
        if disk.size is not None:
            self.add_metric(gauges, disk, 'size', disk.size, labels=common_labels)

        if isinstance(disk.if_attributes, NvmeAttributes):
            #### New Nvme Attributes ####
            for attr_name, attribute in disk.if_attributes.__dict__.items():
                # Ensure the attribute is not None and valid before proceeding
                if isinstance(attribute, (int, float)):
                    attribute_labels = {
                        'name': attr_name,  # Attribute name
                        **common_labels,  # Additional common labels
                    }

                    # Add metric for attribute value
                    self.add_metric(
                        gauges,
                        disk,
                        'attribute_value',
                        attribute,
                        labels=attribute_labels,
                    )
        else:
            #### Old Attributes ####
            for attribute in disk.attributes:
                if attribute is not None:
                    attribute_labels = {
                        'num': str(attribute.num),
                        'name': attribute.name,
                        'flags': str(attribute.flags),
                        'type': attribute.type,
                        'updated': attribute.updated,
                        'whenfailed': attribute.when_failed,
                        **common_labels,
                    }

                    self.add_metric(
                        gauges,
                        disk,
                        'attribute_value',
                        attribute.value_int,
                        labels=attribute_labels,
                    )
                    self.add_metric(
                        gauges,
                        disk,
                        'attribute_thresh',
                        attribute.thresh,
                        labels=attribute_labels,
                    )
                    self.add_metric(
                        gauges,
                        disk,
                        'attribute_worst',
                        attribute.worst,
                        labels=attribute_labels,
                    )
                    if attribute.raw_int is not None:
                        self.add_metric(
                            gauges,
                            disk,
                            'attribute_raw',
                            attribute.raw_int,
                            labels=attribute_labels,
                        )

        #### New Attributes ####
        for diag in vars(disk.diagnostics):
            diag_labels = {**common_labels}

            # Set to -1 if undefined/None
            diag_value = -1 if getattr(disk.diagnostics, diag) is None else getattr(disk.diagnostics, diag)

            self.add_metric(gauges, disk, 'diagnostics_' + diag, diag_value, labels=diag_labels)

        #### Tests ####
        # Supported test types
        self.add_metric(
            gauges,
            disk,
            'test_capabilities',
            disk.test_capabilities,
            labels=common_labels,
            type='state',
        )
        for test in disk.tests:
            test_labels = {
                'num': str(test.num),
                'hours': str(test.hours),
                'type': test.type,
                'status': test.status,
                'LBA': test.LBA,
                **common_labels,
            }

            if test.segment is not None:
                test_labels['segment'] = test.segment
            if test.remain is not None:
                test_labels['remain'] = str(test.remain)
            if test.sense is not None:
                test_labels['sense'] = test.sense
            if test.ASC is not None:
                test_labels['ASC'] = test.ASC
            if test.ASCQ is not None:
                test_labels['ASCQ'] = test.ASCQ

            self.add_metric(gauges, disk, 'test', 1, labels=test_labels)

    def collect(self):
        """
        Collect the metrics.

        Collect the metrics and yield them. Prometheus client library
        uses this method to respond to http queries or save them to disk.
        """
        gauges = {}

        for disk in DeviceList():
            try:
                self.update_pysmart_stats(disk, gauges)
            except Exception as e:
                logging.exception(f'An error occurred while updating pysmart stats for {disk}')

        return gauges.values()
