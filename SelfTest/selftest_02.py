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
from axiom_tc import u07_LiveView_Utils as u07_Utils

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

    # Create objects to u06 and u07 as these will be needed to control self tests and get the results
    u06 = u06_SelfTest(axiom)
    u07 = u07_LiveView(axiom)

    u06.reg_run_test_on_host_trigger_1_ae_baseline_ram_test = 1
    u06.reg_run_test_on_host_trigger_2_ae_internal_ram_test = 1
    u06.reg_run_test_on_host_trigger_3_vdda_test = 1
    u06.reg_run_test_on_host_trigger_4_ae_test = 1
    u06.reg_run_test_on_host_trigger_5_sense_and_shield_pin_leakage_test = 1
    u06.reg_run_test_on_host_trigger_9_crc_check_test = 1
    u06.reg_run_test_on_host_trigger_10_nirq_pin_test = 1
    u06.reg_run_test_on_host_trigger_11_nvm_test = 1
    u06.reg_run_test_on_host_trigger_13_vddc_test = 1
    
    # These self tests require the acquisition engine to be stopped
    axiom.u02.send_command(axiom.u02.CMD_STOP)
    
    # Wait for axiom to report the acquisition engine has stopped
    while True:
        u07.read()
        if u07.reg_ae_status_running == 0:
            break
        sleep(0.1)

    # Send a system manager command to invoke the self tests to run.
    axiom.u02.send_command(axiom.u02.CMD_RUN_SELF_TESTS)

    # Poll u07 to wait for the results to be ready
    while True:
        u07.read()
        if u07.reg_u06_self_test_status == 0: # IDLE
            print("Self Test Complete")
            break
        sleep(0.1)

    # Restart the acquisition engine
    axiom.u02.send_command(axiom.u02.CMD_START)
    while True:
        u07.read()
        if u07.reg_ae_status_running == 1:
            break
        sleep(0.1)

    # Show the results
    u07.read()
    
    print("Test Results:")
    print("  Overall Result : %s" % u07_Utils.convert_self_test_overall_result_to_string(u07.reg_u06_self_test_overall_result))
    print("  Individual Test Results:")
    print("    Test  1 : AE Baseline RAM Test              : %s" % u07_Utils.convert_self_test_result_to_string(u07.reg_u06_self_test_results[1]))
    print("    Test  2 : AE Internal RAM Test              : %s" % u07_Utils.convert_self_test_result_to_string(u07.reg_u06_self_test_results[2]))
    print("    Test  3 : VDDA Test                         : %s" % u07_Utils.convert_self_test_result_to_string(u07.reg_u06_self_test_results[3]))
    print("    Test  4 : AE Test                           : %s" % u07_Utils.convert_self_test_result_to_string(u07.reg_u06_self_test_results[4]))
    print("    Test  5 : Sense and Shield Pin Leakage Test : %s" % u07_Utils.convert_self_test_result_to_string(u07.reg_u06_self_test_results[5]))
    print("    Test  9 : CRC Check Test                    : %s" % u07_Utils.convert_self_test_result_to_string(u07.reg_u06_self_test_results[9]))
    print("    Test 10 : NIRQ Pin Test                     : %s" % u07_Utils.convert_self_test_result_to_string(u07.reg_u06_self_test_results[10]))
    print("    Test 11 : NVM Test                          : %s" % u07_Utils.convert_self_test_result_to_string(u07.reg_u06_self_test_results[11]))
    print("    Test 13 : VDDA Test                         : %s" % u07_Utils.convert_self_test_result_to_string(u07.reg_u06_self_test_results[13]))

    # Close the connection and exit.
    axiom.close()
    sys.exit(0)