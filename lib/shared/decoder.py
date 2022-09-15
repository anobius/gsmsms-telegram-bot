import binascii


class UCS2:
    @classmethod
    def decode(cls, hexstring : str) -> str:
        return binascii.unhexlify(hexstring).decode('utf-16-be');
