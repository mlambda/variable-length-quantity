from typing import Iterable, List, Tuple

from deal import post, pre


class OverflowException(Exception):
    pass


class IncompleteNumberException(Exception):
    pass


N_BITS = 7
CONTINUATION_BIT = 1 << N_BITS
VALUE_BITS = 2 ** N_BITS - 1
UINT32_MAX = 0xFFFF_FFFF


def _extract_first_bits_and_shift(bits: int) -> Tuple[int, int]:
    return bits & VALUE_BITS, bits >> N_BITS


@pre(lambda uint32s: all(0 <= x <= UINT32_MAX for x in uint32s))
def to_bytes(uint32s: Iterable[int]) -> bytes:
    all_numbers = []
    for uint32 in uint32s:
        first_bits, current_bits = _extract_first_bits_and_shift(uint32)
        current_number: List[int] = [first_bits]
        while current_bits:
            first_bits, current_bits = _extract_first_bits_and_shift(current_bits)
            current_number.append(first_bits | CONTINUATION_BIT)
        all_numbers.extend(current_number[::-1])
    return bytes(all_numbers)


@pre(lambda bytes_input: len(bytes_input) > 0)
@post(lambda result: all(x <= UINT32_MAX for x in result))  # pragma: no mutate
def from_bytes(bytes_input: bytes) -> List[int]:
    all_numbers = []
    current_number = 0
    current_offset = 0
    for byte in bytes_input:
        value = byte & VALUE_BITS
        if current_number == 0:
            msb_size = len(bin(value)) - 2
        if current_offset + msb_size > 32:
            raise OverflowException()
        current_number <<= N_BITS
        current_number |= value
        if byte & CONTINUATION_BIT:
            current_offset += N_BITS
        else:
            all_numbers.append(current_number)
            current_number = 0
            current_offset = 0
    if current_offset != 0:
        raise IncompleteNumberException()
    return all_numbers
