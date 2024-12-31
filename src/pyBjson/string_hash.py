def get_JOAAT_hash(string: bytes) -> int:
    hash_ = 0
    for char in string:
        hash_ += char
        hash_ &= 0xFFFFFFFF
        hash_ += (hash_ << 10)
        hash_ &= 0xFFFFFFFF
        hash_ ^= (hash_ >> 6)
    hash_ += (hash_ << 3)
    hash_ &= 0xFFFFFFFF
    hash_ ^= (hash_ >> 11)
    hash_ += (hash_ << 15)
    return hash_ & 0xFFFFFFFF