from __future__ import annotations

import typing as _t

_J = _t.Dict[str, _t.Any]


class SchemaError(Exception): ...


def _type_ok(x, t: str) -> bool:
    return {
        "object": isinstance(x, dict),
        "array": isinstance(x, list),
        "string": isinstance(x, str),
        "integer": isinstance(x, int) and not isinstance(x, bool),
        "number": isinstance(x, (int, float)) and not isinstance(x, bool),
        "boolean": isinstance(x, bool),
        "null": x is None,
    }.get(t, False)


def _validate(obj, schema: _J, path="$", errs=None):
    if errs is None:
        errs = []
    st = schema.get("type")
    if isinstance(st, list):
        if not any(_type_ok(obj, t) for t in st):
            errs.append(f"{path}: type mismatch, expected one of {st}, got {type(obj).__name__}")
            return errs
    elif isinstance(st, str):
        if not _type_ok(obj, st):
            errs.append(f"{path}: type mismatch, expected {st}, got {type(obj).__name__}")
            return errs
    # object rules
    if isinstance(obj, dict):
        req = schema.get("required", [])
        for k in req:
            if k not in obj:
                errs.append(f"{path}: missing required property '{k}'")
        props: _J = schema.get("properties", {})
        addl = schema.get("additionalProperties", True)
        for k, v in obj.items():
            if k in props:
                _validate(v, props[k], f"{path}.{k}", errs)
            else:
                if addl is False:
                    errs.append(f"{path}: additionalProperties not allowed: '{k}'")
                elif isinstance(addl, dict):
                    _validate(v, addl, f"{path}.{k}", errs)
    # array rules
    if isinstance(obj, list):
        items = schema.get("items")
        if isinstance(items, dict):
            for i, it in enumerate(obj):
                _validate(it, items, f"{path}[{i}]", errs)
        elif isinstance(items, list):
            for i, sch in enumerate(items):
                if i < len(obj):
                    _validate(obj[i], sch, f"{path}[{i}]", errs)
    return errs


def validate(obj, schema: _J) -> _t.List[str]:
    if not isinstance(schema, dict):
        raise SchemaError("schema must be an object")
    return _validate(obj, schema, "$", [])
