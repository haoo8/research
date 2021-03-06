def serialize(val, typ):
    if typ in ('hash32', 'address'):
        assert len(val) == 20 if typ == 'address' else 32
        return val
    elif typ[:3] == 'int':
        length = int(typ[3:])
        assert length % 8 == 0
        return val.to_bytes(length // 8, 'big')
    elif typ == 'bytes':
        return len(val).to_bytes(4, 'big') + val
    elif isinstance(typ, list):
        assert len(typ) == 1
        sub = b''.join([serialize(x, typ[0]) for x in val])
        return len(sub).to_bytes(4, 'big') + sub
    elif isinstance(typ, type):
        sub = b''.join([serialize(getattr(val, k), typ.fields[k]) for k in sorted(typ.fields.keys())])
        return len(sub).to_bytes(4, 'big') + sub

def _deserialize(data, start, typ):
    if typ in ('hash32', 'address'):
        length = 20 if typ == 'address' else 32
        assert len(data) + start >= length
        return data[start: start+length], start+length
    elif typ[:3] == 'int':
        length = int(typ[3:])
        assert length % 8 == 0
        assert len(data) + start >= length // 8
        return int.from_bytes(data[start: start+length//8], 'big'), start+length//8
    elif typ == 'bytes':
        length = int.from_bytes(data[start:start+4], 'big')
        assert len(data) + start >= 4+length
        return data[start+4: start+4+length], start+4+length
    elif isinstance(typ, list):
        assert len(typ) == 1
        length = int.from_bytes(data[start:start+4])
        pos, o = start + 4, []
        while pos < start + 4 + length:
            result, pos = _deserialize(data, pos, typ[0])
            o.append(result)
        assert pos == start + 4 + length
        return o, pos
    elif isinstance(typ, type):
        values = {}
        pos = start
        for k in sorted(typ.fields.keys()):
            values[k], pos = _deserialize(data, pos, typ.fields[k])
        return typ(**values), pos

def deserialize(data, typ):
    return _deserialize(data, 0, typ)[0]
