#!/usr/bin/env python3
################################################################################
# MIT License
# 
# Copyright (c) 2023 TouchNetix
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
################################################################################

import sys
import argparse
from time import sleep

from axiom_tc import axiom
from axiom_tc import u06_SelfTest
from axiom_tc import u07_LiveView

def init_axiom_comms(args):
    # Import the requested comms layer
    if args.i == "i2c":
        if args.i2c_bus == None or args.i2c_address == None:
            print("The I2C bus and the I2C address arguments need to be specified.")
            parser.print_help()
            sys.exit(-1)
        else:
            from axiom_tc.I2C_Comms import I2C_Comms
            comms = I2C_Comms(args.i2c_bus, int(args.i2c_address, 16))

    elif args.i == "spi":
        if args.spi_bus == None or args.spi_device == None:
            print("The SPI bus and the SPI device arguments need to be specified.")
            parser.print_help()
            sys.exit(-1)
        else:
            from axiom_tc.SPI_Comms import SPI_Comms
            comms = SPI_Comms(args.spi_bus, args.spi_device)

    elif args.i == "usb":
            from axiom_tc.USB_Comms import USB_Comms
            comms = USB_Comms()

    else:
        raise Exception("Unsupported comms interface")

    # When instantiating the aXiom object, pass in the comms object which will
    # provide access to the low level reads and write methods.
    return axiom(comms)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Utility to configure and get aXiom self test results')
    parser.add_argument("-i", help='comms interface to communicate with aXiom', choices=["spi", "i2c", "usb"], required=True, type=str)
    parser.add_argument("--i2c-bus", help='I2C bus number, as per `/dev/i2c-<bus>`', metavar='BUS', required=False, type=int)
    parser.add_argument("--i2c-address", help='I2C address, either 0x66 or 0x67', choices=["0x66", "0x67"], metavar='ADDR', required=False, type=str)
    parser.add_argument("--spi-bus", help='SPI bus number, as per `/dev/spi<bus>.<device>`', metavar='BUS', required=False, type=int)
    parser.add_argument("--spi-device", help='SPI device for CS, as per `/dev/spi<bus>.<device>`', metavar='DEV', required=False, type=int)
    args = parser.parse_args()

    # Create axiom object
    axiom = init_axiom_comms(args)

    # Create objects for u06 and u07. u06 configures the self test and u07 is
    # where the self test results are.
    u06 = u06_SelfTest(axiom)
    u07 = u07_LiveView(axiom)

    # Enable the self test to validate CRCs if it is not already enabled.
    if u06.reg_run_test_on_host_trigger_9_crc_check_test == 0:
        u06.reg_run_test_on_host_trigger_9_crc_check_test = 1
        # The change will need to be written to NVM, otherwise this test will
        # fail as we have just changed the RAM configuration but not the NVM.
        u06.write(True)

    # Send a system manager command to invoke the self tests to run.
    axiom.u02.send_command(axiom.u02.CMD_RUN_SELF_TESTS)

    # Wait for the self test results to run. u07 reports the status of self
    # test. 
    while True:
        u07.read()
        if u07.reg_u06_self_test_status == 0: # IDLE
            print("Self Test Complete")
            break
        sleep(0.1)

    # Print out u07 live data to see the results
    u07.print()
    
    # Close the connection and exit.
    axiom.close()
    sleep(0.1)
    sys.exit(0)