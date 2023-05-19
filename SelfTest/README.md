# Self Test Examples

A collection of examples on how to use self test features within aXiom.

## Reference Material

App Note: TNxAN00056 aXiom Self Test

## `selftest_01.py`

`selftest_01.py` will configure aXiom to run self test #9 CRC Generate and Check when instructed by the host. This test will regenerate all CRC's and confirm that they match what is stored in flash.

## `selftest_02.py`

`selftest_02.py` demonstrates a slightly more complex self test sequence. To run some of the self tests, they require the acquisition engine (AE) to be stopped (see TNxAN00056). This test sequence will select the self tests to run, stop the AE and then perform the self test. Once the self test is complete, the AE will be restarted so that touch screen measurements can continue.

## Prerequisites

### axiom_tc Package

The `axiom_tc` python package is required to run these examples. Use the `requirements.txt` to install this package.

```console
pip install -r requirements.txt
```

### SPI Interface

Requires `spidev` to be installed and accessible to your Python interpreter.

```console
pip install spidev
```

See [spidev](https://pypi.org/project/spidev/) for more information.

### I2C Interface

Requires `smbus2` to be installed and accessible to your Python interpreter.

```console
pip install smbus2
```

See [smbus2](https://pypi.org/project/smbus2/) for more information.

### USB Interface

Requires `hid` to be installed and accessible to your Python interpreter.
You will usually need sudo access for this, so:

```console
sudo python3 -m pip install hid
```

See [hid](https://pypi.org/project/hid/) for more information.
