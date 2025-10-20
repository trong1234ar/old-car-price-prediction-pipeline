from typing import get_origin, get_args, Union
from pyspark.sql import types as T

def _py_to_spark(t):
    if get_origin(t) is Union:  # unwrap Optional[X]
        t = [a for a in get_args(t) if a is not type(None)][0]
    return {
        str:  T.StringType(),
        int:  T.LongType(),
        float:T.DoubleType(),
        bool: T.BooleanType(),
    }.get(t, T.StringType())

def pydantic_to_schema(model_cls) -> T.StructType:
    fields = getattr(model_cls, "model_fields", None) or getattr(model_cls, "__fields__")  # v2 / v1
    struct = []
    for name, f in fields.items():
        ann = getattr(f, "annotation", None) or getattr(f, "type_", str)
        struct.append(T.StructField(name, _py_to_spark(ann), True))
    return T.StructType(struct)