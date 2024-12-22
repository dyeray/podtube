import xxhash

class Hasher:
    def hash(self, data: str) -> str:
        return xxhash.xxh3_64_hexdigest(data)
