from base64 import urlsafe_b64encode, urlsafe_b64decode


def num_bytes_required(num, max_byte_value=256):
    """Return the number of bytes required to represent the given number.

    >>> num_bytes_required(255)
    1
    >>> num_bytes_required(256)
    2
    >>> num_bytes_required(4_294_967_295)
    4
    >>> num_bytes_required(4_294_967_296)
    5
    """
    i = 1
    while num >= max_byte_value:
        num = num // max_byte_value
        i += 1
    return i


def encode(num):
    """Encode an int using base64.

    >>> encode(256)
    'AQA'
    """
    array_size = num_bytes_required(num)
    bytes_array = num.to_bytes(array_size, byteorder="big", signed=False)

    as_b64 = urlsafe_b64encode(bytes_array)
    return as_b64.decode("utf-8").rstrip("=")


def decode(encoded_str):
    """Decode an int using bas64.

    >>> decode("AQA")
    256
    """
    while len(encoded_str) % 4 != 0:
        encoded_str += "="

    bytes_array = urlsafe_b64decode(encoded_str.encode("utf-8"))
    return int.from_bytes(bytes_array, byteorder="big", signed=False)
