from __future__ import absolute_import, division, print_function
import struct
from ctypes import *
from ctypes.wintypes import HGLOBAL
from ctypes.util import find_library
import time
from mcculw import ul

_ERRSTRLEN = 256

# Load the correct library based on the Python architecture in use
is_32bit = struct.calcsize("P") == 4
dll_file_name = "cbw32.dll" if is_32bit else "cbw64.dll"
dll_absolute_path = find_library(dll_file_name)
if dll_absolute_path is None:
    dll_absolute_path = dll_file_name
_cbw = WinDLL(dll_absolute_path)


class ULError(Exception):
    def __init__(self, errorcode):
        super(ULError, self).__init__()
        self.errorcode = errorcode
        self.message = get_err_msg(errorcode)

    def __str__(self):
        return "Error " + str(self.errorcode) + ": " + self.message


def get_err_msg(error_code):

    msg = create_string_buffer(_ERRSTRLEN)
    _check_err(_cbw.cbGetErrMsg(error_code, msg))
    return msg.value.decode("utf-8")


def _check_err(errcode):
    if errcode:
        raise ULError(errcode)


# https://kb.mccdaq.com/Print50766.aspx

# These are the expected arguement types that the C code is expecting
_cbw.cbC7266Config.argtypes = [
    c_int,
    c_int,
    c_int,
    c_int,
    c_int,
    c_int,
    c_int,
    c_int,
    c_int,
]


def cb_C7266_config(
    board_num: int,
    counter_num: int,
    quadrature: int,
    counting_mode: int,
    data_encoding: int,
    index_mode: int,
    invert_index: int,
    flag_pins: int,
    gating: int,
) -> None:
    """
    Implements the no longer supported functionality for the C7266 Encoders.

    Args:
        board_num (int): Encoder board number as defined in Instacal.
        counter_num (int): Counter channel number.
        quadrature (int): Resolution to read the values at. Range from 0 to 4.
        counting_mode (int): _description_
        data_encoding (int): _description_
        index_mode (int): _description_
        invert_index (int): _description_
        flag_pins (int): _description_
        gating (int): _description_
    """
    _check_err(
        _cbw.cbC7266Config(
            board_num,
            counter_num,
            quadrature,
            counting_mode,
            data_encoding,
            index_mode,
            invert_index,
            flag_pins,
            gating,
        )
    )


_cbw.cbCClear.argtypes = [c_int, c_int]


def cb_CClear(board_num, counter_num):
    """
    Resets the current encoder values to zero.

    Args:
        board_num (int): Encoder board number as defined in Instacal.
        counter_num (int): Encoder counter channel number.
    """
    _check_err(_cbw.cbCClear(board_num, counter_num))


_cbw.cbCIn.argtypes = [c_int, c_int, POINTER(c_ushort)]


def cb_CIn(board_num, counter_num):
    """
    Reads the current count from a counter channel. Outputs as an unsigned short
    with values between 0 and 65535 (16-bit).

    Args:
        board_num (int): The number associated with the board.
        board_num may be 0 to 99. The specified board must have a counter.
        counter_num (int): The counter to read the current count from.

    Returns:
        count: Counter value.
    """
    count_value = c_ushort()
    _check_err(_cbw.cbCIn(board_num, counter_num, byref(count_value)))
    return count_value.value


_cbw.cbCIn32.argtypes = [c_int, c_int, POINTER(c_ulong)]


def cb_CIn32(board_num, counter_num):

    count_value = c_ulong()
    _check_err(_cbw.cbCIn32(board_num, counter_num, byref(count_value)))
    return count_value.value


_cbw.cbCInScan.argtypes = [c_int, c_int, c_int, c_long, POINTER(c_long), c_int, c_int]


def cb_CInScan(board_num, counter_first, counter_last, count, mem_handle, options):

    rate_value = c_long()
    _check_err(
        _cbw.cbCInScan(
            board_num,
            counter_first,
            counter_last,
            count,
            byref(rate_value),
            mem_handle,
            options,
        )
    )
    return rate_value.value


_cbw.cbCStatus.argtypes = [c_int, c_int, POINTER(c_ulong)]


def cb_CStatus(board_num, counter_num):

    status_value = c_ulong()
    _check_err(_cbw.cbCStatus(board_num, counter_num, byref(status_value)))
    return status_value.value


_cbw.cbCLoad32.argtypes = [c_int, c_int, c_ulong]


def testing_cb(board_num, reg_num, load_value):

    _check_err(_cbw.cbCLoad32())
    return 0


if __name__ == "__main__":

    # Encoders are set to unsigned short and output values 0 to 65536
    # Configure the 4 channels of the QUAD04 Encoder
    # Quadrature value of 4 is highest resolution
    cb_C7266_config(0, 1, 4, 0, 2, 0, 0, 1, 0)
    cb_C7266_config(0, 2, 4, 0, 2, 0, 0, 1, 0)
    cb_C7266_config(0, 3, 0, 0, 2, 0, 0, 1, 0)
    cb_C7266_config(0, 4, 0, 0, 2, 0, 0, 1, 0)

    # Read in values from the encoder
    while True:
        print(ul.c_in(0, 2))
        time.sleep(1)
