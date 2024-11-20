  
# pySMART-exporter

![](https://img.shields.io/pypi/v/pySMART-exporter?label=release)
![](https://img.shields.io/pypi/pyversions/pySMART-exporter)
![](https://img.shields.io/github/actions/workflow/status/Naudit/pySMART-exporter/publish-to-pypi.yml)
![](https://img.shields.io/github/issues/Naudit/pySMART-exporter)
![](https://img.shields.io/github/issues-pr/Naudit/pySMART-exporter)
![](https://img.shields.io/pypi/dm/pysmart-exporter)

Copyright (C) 2021 Rafael Leira, Naudit HPCN S.L.

`pySMART-exporter` is a Python Prometheus exporter for collecting and exposing S.M.A.R.T. metrics of storage devices. It leverages the [pySMART library](https://github.com/truenas/py-SMART) and integrates Prometheus client library functionalities for HTTP publication or file-based metric exports.

---

## Features

- Collects S.M.A.R.T. metrics from storage devices.
- Supports Prometheus integration via HTTP or text-based node collector files.
- Includes support for various storage interfaces, including NVMe attributes and diagnostics.

---

## Installation

The `pySMART-exporter` can be installed via PyPI:

```bash
python -m pip install pySMART-exporter
```

Ensure that `smartctl` from the `smartmontools` package is installed, as it is a prerequisite. For most Linux distributions, use your package manager:

```bash
sudo apt-get install smartmontools

# or

sudo yum install smartmontools
```

---

## Usage

The exporter supports two modes: **server mode** (HTTP) and **file mode** (node exporter textfile). It should run as a privileged user to access disk information.

### Server Mode

To run the exporter in server mode, execute the following command:

```bash
pysmart_exporter -l 0.0.0.0:9099
```

Then configure Prometheus to scrape metrics from the endpoint.

### File Mode

To generate a one-time metric file for use with a Prometheus node exporter:

```bash
pysmart_exporter -f /path/to/output/file.txt -1
```

To continuously generate metric files at a set interval (e.g., 60 seconds):

```bash
pysmart_exporter -f /path/to/output/file.txt -i 60
```

---

## Example Metrics Output

Below is a sample of the metrics exposed by `pySMART-exporter`:

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
pysmart_test_capabilities{device="nvme0",interface="nvme",pysmart_test_capabilities="short"} 1.0
```

---

## CLI Options

| Option | Description |
|-----------------------|--------------------------------------------------------------------------------------------------|
| `-f`, `--textfile-name` | Path to the file where metrics will be stored for node collection. |
| `-l`, `--listen` | Host and port to listen on in HTTP server mode (e.g., `0.0.0.0:9417`). |
| `-i`, `--interval` | Interval (in seconds) between metric updates. Default: `60`. |
| `-1`, `--oneshot` | Run only once and exit (useful for cron jobs). |
| `-q`, `--quiet` | Suppress error messages and warnings. |
| `--include` | Comma-separated list of devices to include (e.g., `nvme0,/dev/sda`). |
| `--exclude` | Comma-separated list of devices to exclude. |
| `--metric-prefix` | Custom prefix for metrics. Default: `pysmart`. |
| `--metrics` | Comma-separated list of specific metrics to export (e.g., `temperature,size,assessment_passed`).|

---

## Metrics

| **Metric Name** | **Type** | **Description** | **Labels** |
|---|---|---|---|
|`pysmart_info`|`info`|General information about the disk, including model, firmware, size, and other static attributes.|`device`, `interface`, `model`, `serial`, `firmware`, `rotation`, `size_raw`, `size`, `ssd`, `smart_capable`, `smart_enabled`, `vendor`, `sector_size`, and more.|
|`pysmart_assessment_passed`|`gauge`|Assessment of the disk's health. `1` for PASS, `0` otherwise.|`device`, `interface`|
|`pysmart_temperature`|`gauge`|Current temperature of the disk in Celsius.|`device`, `interface`|
|`pysmart_size`|`gauge`|Disk size in bytes.|`device`, `interface`|
|`pysmart_attribute_value`|`gauge`|SMART attribute values such as error counts, read/write metrics, etc.|`device`, `name` (attribute name), `num`, `type`, `flags`, `updated`, `whenfailed`, and more depending on attribute.|
|`pysmart_attribute_thresh`|`gauge`|Threshold values for SMART attributes.|Similar to `pysmart_attribute_value`|
|`pysmart_attribute_worst`|`gauge`|The worst recorded value for a given SMART attribute.|Similar to `pysmart_attribute_value`|
|`pysmart_attribute_raw`|`gauge`|The raw value for a SMART attribute.|Similar to `pysmart_attribute_value`|
|`pysmart_diagnostics_*`|`gauge`|Disk diagnostic statistics, including errors and other health-related data.|`device`, `interface`|
|`pysmart_test_capabilities`|`state`|Types of self-tests supported by the disk (e.g., short, long, offline).|`device`, `interface`|
|`pysmart_test`|`gauge`|Details about completed or pending disk self-tests.|`device`, `type` (test type), `status`, `hours`, `num`, and other self-test details.|  

  ---

## Installation

``pySMART-exporter`` is available on PyPI and installable via ``pip``::

    python -m pip install pySMART-exporter

The only external (non-python) dependency is the ``smartctl`` component of the smartmontools package.  This should be pre-installed in most Linux distributions, or it can be obtained through your package manager.  Likely one of the following::

    apt-get install smartmontools
        or
    yum install smartmontools


## License

This program is distributed under the terms of the license specified in the [LICENSE](./LICENSE) file.

---

## References

- [pySMART Library](https://github.com/truenas/py-SMART)

- [Prometheus Documentation](https://prometheus.io/docs/)

- [SMART Monitoring Tools](https://www.smartmontools.org/)
