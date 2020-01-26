class PlayerProtocol:
    def __init__(self):
        pass

    @staticmethod
    def encode(bytestring):
        length = len(bytestring)
        return (length).to_bytes(4, byteorder="little", signed=False) + bytestring

    @staticmethod
    def decode(byte):
        length = int.from_bytes(byte[:4], byteorder="little", signed=False)
        return length, byte[4:]

