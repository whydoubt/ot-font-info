#!/usr/bin/env python3

import sys
from struct import unpack


verbose = False


def _verify_checksum(data, checksum):
    pass


_handlers = {}
def handles(tag):
    def real_handles(func):
        def wrapped(data):
            func(tag, data)
        _handlers[tag] = wrapped
        return func
    return real_handles


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == '-v':
        verbose = True
        sys.argv.pop(1)

    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} [-v] font.ttf')
        exit()

    with open(sys.argv[1], 'rb') as f:
        (scaler_type, num_tables, search_range, entry_selector,
                range_shift) = unpack('>IHHHH', f.read(12))
        tables = []
        for _ in range(num_tables):
            tables.append(unpack('>4sIII', f.read(16)))

        for tag, checksum, offset, length in tables:
            if tag in _handlers:
                f.seek(offset)
                data = f.read(length)
                _verify_checksum(data, checksum)
                _handlers[tag](data)
            else:
                print(f'Table {tag} has no handler. Ignoring.')
