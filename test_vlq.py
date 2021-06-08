from typing import List

from deal import PreContractError
from hypothesis import given
from hypothesis.strategies import integers, lists
from pytest import raises

from vlq import from_bytes, IncompleteNumberException, OverflowException, to_bytes


def test_to_single_byte() -> None:
    assert b"\x00" == to_bytes([0])
    assert b"\x40" == to_bytes([0x40])
    assert b"\x7F" == to_bytes([0x7F])


def test_to_double_byte() -> None:
    assert b"\x81\x00" == to_bytes([0x80])
    assert b"\xC0\x00" == to_bytes([0x2000])
    assert b"\xFF\x7F" == to_bytes([0x3FFF])


def test_to_bytes_uint32_overflow() -> None:
    with raises(PreContractError):
        to_bytes([2 ** 32])
    to_bytes([2 ** 32 - 1])


def test_to_triple_byte() -> None:
    assert b"\x81\x80\x00" == to_bytes([0x4000])
    assert b"\xC0\x80\x00" == to_bytes([0x10_0000])
    assert b"\xFF\xFF\x7F" == to_bytes([0x1F_FFFF])


def test_to_quadruple_byte() -> None:
    assert b"\x81\x80\x80\x00" == to_bytes([0x20_0000])
    assert b"\xC0\x80\x80\x00" == to_bytes([0x0800_0000])
    assert b"\xFF\xFF\xFF\x7F" == to_bytes([0x0FFF_FFFF])


def test_to_quintuple_byte() -> None:
    assert b"\x81\x80\x80\x80\x00" == to_bytes([0x1000_0000])
    assert b"\x8F\xF8\x80\x80\x00" == to_bytes([0xFF00_0000])
    assert b"\x8F\xFF\xFF\xFF\x7F" == to_bytes([0xFFFF_FFFF])


def test_from_bytes() -> None:
    assert [0x7F] == from_bytes(b"\x7F")
    assert [0x2000] == from_bytes(b"\xC0\x00")
    assert [0x1F_FFFF] == from_bytes(b"\xFF\xFF\x7F")
    assert [0x20_0000] == from_bytes(b"\x81\x80\x80\x00")
    assert [0xFFFF_FFFF] == from_bytes(b"\x8F\xFF\xFF\xFF\x7F")


def test_to_bytes_multiple_values() -> None:
    assert b"\x40\x7F" == to_bytes([0x40, 0x7F])
    assert b"\x81\x80\x00\xC8\xE8\x56" == to_bytes([0x4000, 0x12_3456])
    assert b"\xC0\x00\xC8\xE8\x56\xFF\xFF\xFF\x7F\x00\xFF\x7F\x81\x80\x00" == to_bytes(
        [0x2000, 0x12_3456, 0x0FFF_FFFF, 0x00, 0x3FFF, 0x4000]
    )


def test_from_bytes_multiple_values() -> None:
    assert [0x2000, 0x12_3456, 0x0FFF_FFFF, 0x00, 0x3FFF, 0x4000] == from_bytes(
        b"\xC0\x00\xC8\xE8\x56\xFF\xFF\xFF\x7F\x00\xFF\x7F\x81\x80\x00"
    )


def test_incomplete_byte_sequence() -> None:
    with raises(IncompleteNumberException):
        from_bytes(b"\xFF")


def test_zero_incomplete_byte_sequence() -> None:
    with raises(IncompleteNumberException):
        from_bytes(b"\x80")


def test_from_bytes_overflow_uint32() -> None:
    with raises(OverflowException):
        from_bytes(b"\x9F\xFF\xFF\xFF\x7F")
    from_bytes(b"\x8F\xFF\xFF\xFF\x7F")


def test_chained_execution_is_identity() -> None:
    to_test = [0, 93213, 2, 123, 5821, 51243, 66123]
    assert to_test == from_bytes(to_bytes(to_test))


def test_empty_byte() -> None:
    with raises(PreContractError):
        from_bytes(b"")


@given(lists(integers(min_value=0, max_value=255), min_size=1))
def test_chained_execution_is_identity_gen(input_list: List[int]) -> None:
    assert from_bytes(to_bytes(input_list)) == input_list
