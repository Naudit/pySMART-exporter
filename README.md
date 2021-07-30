pySMART-exporter
===========

![](https://img.shields.io/pypi/v/pySMART-exporter?label=release)
![](https://img.shields.io/pypi/pyversions/pySMART-exporter)
![](https://img.shields.io/github/workflow/status/Naudit/pySMART-exporter/Publish%20Python%20%F0%9F%90%8D%20distributions%20%F0%9F%93%A6%20to%20PyPI%20and%20TestPyPI)
![](https://img.shields.io/github/issues/Naudit/pySMART-exporter)
![](https://img.shields.io/github/issues-pr/Naudit/pySMART-exporter)
![](https://img.shields.io/pypi/dm/pysmart-exporter)

Copyright (C) 2021 Naudit HPCN S.L.

PySMART-exporter is a simple Python prometheus exporter built on top of [PySMART library](https://github.com/truenas/py-SMART).


Usage
=====

Server mode
-----------
To Use the exporter in server mode you can simply run as

`pysmart_exporter -l 0.0.0.0:9099`

And configure your prometheus to access it.

File mode
---------
If you whish to generate just a metric sample, you can run this:

`pysmart_exporter -f out.txt -1`

It may generate a file with a similar content as:

```prometheus
# HELP pysmart_info PySMART metric info
# TYPE pysmart_info gauge
pysmart_info{device="nvme0",firmware="ADHA0101",interface="nvme",model="KBG30ZMV256G TOSHIBA",rotation="None",serial="*********12P",size="256000000000",size_raw="256 GB",smart_capable="True",smart_enabled="True",ssd="True"} 1.0
# HELP pysmart_assessment PySMART metric assessment
# TYPE pysmart_assessment gauge
pysmart_assessment{device="nvme0",interface="nvme",pysmart_assessment="PASS"} 1.0
# HELP pysmart_temperature PySMART metric temperature
# TYPE pysmart_temperature gauge
pysmart_temperature{device="nvme0",interface="nvme"} 44.0
# HELP pysmart_size PySMART metric size
# TYPE pysmart_size gauge
pysmart_size{device="nvme0",interface="nvme"} 2.56e+011
# HELP pysmart_test_capabilities PySMART metric test_capabilities
# TYPE pysmart_test_capabilities gauge
pysmart_test_capabilities{device="nvme0",interface="nvme",pysmart_test_capabilities="conveyance"} 0.0
pysmart_test_capabilities{device="nvme0",interface="nvme",pysmart_test_capabilities="long"} 0.0
pysmart_test_capabilities{device="nvme0",interface="nvme",pysmart_test_capabilities="offline"} 0.0
pysmart_test_capabilities{device="nvme0",interface="nvme",pysmart_test_capabilities="selective"} 0.0
pysmart_test_capabilities{device="nvme0",interface="nvme",pysmart_test_capabilities="short"} 0.0
```

You can also set an interval with `-i` instead of `-1` to keep flushing data every n seconds

Installation
============
``pySMART-exporter`` is available on PyPI and installable via ``pip``::

    python -m pip install pySMART-exporter

The only external (non-python) dependency is the ``smartctl`` component of the smartmontools package.  This should be pre-installed in most Linux distributions, or it can be obtained through your package manager.  Likely one of the following::

    apt-get install smartmontools
        or
    yum install smartmontools

