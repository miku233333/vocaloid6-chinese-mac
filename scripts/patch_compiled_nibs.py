#!/usr/bin/env python3
"""
VOCALOID6 compiled nib 定向補丁工具

用途：
- 解析 keyedobjects-*.nib 內的 NIBArchive
- 對特定 NSString 的 NS.bytes 做精準替換
- 重新序列化並寫回檔案

目前主要用於：
- VEHomeWC 啟動畫面的固定英文文案
"""

from __future__ import annotations

import argparse
import json
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MAGIC_BYTES = b"NIBArchive"

TYPE_INT8 = 0
TYPE_INT16 = 1
TYPE_INT32 = 2
TYPE_INT64 = 3
TYPE_BOOL_TRUE = 4
TYPE_BOOL_FALSE = 5
TYPE_FLOAT = 6
TYPE_DOUBLE = 7
TYPE_DATA = 8
TYPE_NIL = 9
TYPE_OBJECT_REF = 10


@dataclass
class Header:
    unknown_1: int
    unknown_2: int
    object_count: int
    offset_objects: int
    key_count: int
    offset_keys: int
    value_count: int
    offset_values: int
    class_name_count: int
    offset_class_names: int


@dataclass
class Obj:
    class_name_index: int
    values_index: int
    value_count: int


@dataclass
class Key:
    name: str

    @property
    def length(self) -> int:
        return len(self.name)


@dataclass
class ClassName:
    name: str
    extras: list[int]

    @property
    def length(self) -> int:
        return len(self.name.encode("utf-8")) + 1

    @property
    def extras_count(self) -> int:
        return len(self.extras)


@dataclass
class Value:
    key_index: int
    type_code: int
    data: Any = None


@dataclass
class Archive:
    header: Header
    objects: list[Obj]
    keys: list[Key]
    values: list[Value]
    class_names: list[ClassName]


def decode_varint(blob: bytes, offset: int) -> tuple[int, int]:
    result = 0
    shift = 0
    while True:
        current = blob[offset]
        offset += 1
        result |= (current & 0x7F) << shift
        if current & 0x80:
            return result, offset
        shift += 7


def encode_varint(value: int) -> bytes:
    if value < 0:
        raise ValueError(f"varint must be >= 0, got {value}")
    out = bytearray()
    while True:
        current = value & 0x7F
        value >>= 7
        if value == 0:
            out.append(current | 0x80)
            return bytes(out)
        out.append(current)


def parse_archive(path: Path) -> Archive:
    blob = path.read_bytes()
    if not blob.startswith(MAGIC_BYTES):
        raise ValueError(f"not a NIBArchive file: {path}")

    header = Header(*struct.unpack_from("<10i", blob, len(MAGIC_BYTES)))
    offset = len(MAGIC_BYTES) + 40

    objects: list[Obj] = []
    for _ in range(header.object_count):
        class_name_index, offset = decode_varint(blob, offset)
        values_index, offset = decode_varint(blob, offset)
        value_count, offset = decode_varint(blob, offset)
        objects.append(Obj(class_name_index, values_index, value_count))

    keys: list[Key] = []
    for _ in range(header.key_count):
        length, offset = decode_varint(blob, offset)
        name = blob[offset:offset + length].decode("utf-8")
        offset += length
        keys.append(Key(name))

    values: list[Value] = []
    for _ in range(header.value_count):
        key_index, offset = decode_varint(blob, offset)
        type_code = blob[offset]
        offset += 1
        if type_code == TYPE_INT8:
            data = blob[offset]
            offset += 1
        elif type_code == TYPE_INT16:
            data = struct.unpack_from("<h", blob, offset)[0]
            offset += 2
        elif type_code == TYPE_INT32:
            data = struct.unpack_from("<i", blob, offset)[0]
            offset += 4
        elif type_code == TYPE_INT64:
            data = struct.unpack_from("<q", blob, offset)[0]
            offset += 8
        elif type_code in (TYPE_BOOL_TRUE, TYPE_BOOL_FALSE):
            data = type_code == TYPE_BOOL_TRUE
        elif type_code == TYPE_FLOAT:
            data = struct.unpack_from("<f", blob, offset)[0]
            offset += 4
        elif type_code == TYPE_DOUBLE:
            data = struct.unpack_from("<d", blob, offset)[0]
            offset += 8
        elif type_code == TYPE_DATA:
            length, offset = decode_varint(blob, offset)
            data = blob[offset:offset + length]
            offset += length
        elif type_code == TYPE_NIL:
            data = None
        elif type_code == TYPE_OBJECT_REF:
            data = struct.unpack_from("<i", blob, offset)[0]
            offset += 4
        else:
            raise ValueError(f"unsupported value type {type_code} in {path}")
        values.append(Value(key_index, type_code, data))

    class_names: list[ClassName] = []
    for _ in range(header.class_name_count):
        length, offset = decode_varint(blob, offset)
        extras_count, offset = decode_varint(blob, offset)
        extras = []
        if extras_count:
            extras = list(struct.unpack_from("<" + "i" * extras_count, blob, offset))
            offset += 4 * extras_count
        name_blob = blob[offset:offset + length]
        offset += length
        class_names.append(ClassName(name_blob[:-1].decode("utf-8"), extras))

    return Archive(header, objects, keys, values, class_names)


def serialize_archive(archive: Archive) -> bytes:
    objects_blob = b"".join(
        encode_varint(obj.class_name_index)
        + encode_varint(obj.values_index)
        + encode_varint(obj.value_count)
        for obj in archive.objects
    )
    keys_blob = b"".join(
        encode_varint(key.length) + key.name.encode("utf-8")
        for key in archive.keys
    )

    def encode_value(value: Value) -> bytes:
        prefix = encode_varint(value.key_index) + bytes([value.type_code])
        if value.type_code == TYPE_INT8:
            payload = bytes([value.data])
        elif value.type_code == TYPE_INT16:
            payload = struct.pack("<h", value.data)
        elif value.type_code == TYPE_INT32:
            payload = struct.pack("<i", value.data)
        elif value.type_code == TYPE_INT64:
            payload = struct.pack("<q", value.data)
        elif value.type_code in (TYPE_BOOL_TRUE, TYPE_BOOL_FALSE, TYPE_NIL):
            payload = b""
        elif value.type_code == TYPE_FLOAT:
            payload = struct.pack("<f", value.data)
        elif value.type_code == TYPE_DOUBLE:
            payload = struct.pack("<d", value.data)
        elif value.type_code == TYPE_DATA:
            payload = encode_varint(len(value.data)) + value.data
        elif value.type_code == TYPE_OBJECT_REF:
            payload = struct.pack("<i", value.data)
        else:
            raise ValueError(f"unsupported value type {value.type_code}")
        return prefix + payload

    values_blob = b"".join(encode_value(value) for value in archive.values)
    class_blob = b"".join(
        encode_varint(class_name.length)
        + encode_varint(class_name.extras_count)
        + struct.pack("<" + "i" * len(class_name.extras), *class_name.extras)
        + class_name.name.encode("utf-8")
        + b"\0"
        for class_name in archive.class_names
    )

    offset_objects = len(MAGIC_BYTES) + 40
    offset_keys = offset_objects + len(objects_blob)
    offset_values = offset_keys + len(keys_blob)
    offset_class_names = offset_values + len(values_blob)
    header = struct.pack(
        "<10i",
        archive.header.unknown_1,
        archive.header.unknown_2,
        len(archive.objects),
        offset_objects,
        len(archive.keys),
        offset_keys,
        len(archive.values),
        offset_values,
        len(archive.class_names),
        offset_class_names,
    )
    return MAGIC_BYTES + header + objects_blob + keys_blob + values_blob + class_blob


class CompiledNibPatcher:
    def __init__(self, language: str = "zh-TW", config_path: str | Path | None = None):
        self.language = language
        default_config = Path(__file__).resolve().parent.parent / "data" / "glossaries" / f"compiled-nib-{language}.json"
        self.config_path = Path(config_path).expanduser() if config_path else default_config
        self.patches = self._load_patches()

    def _load_patches(self) -> dict[str, dict[str, str]]:
        if not self.config_path.exists():
            return {}
        with open(self.config_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return payload.get("patches", {})

    def patch_archive_file(self, path: Path, replacements: dict[str, str]) -> list[tuple[int, str, str]]:
        archive = parse_archive(path)
        changed: list[tuple[int, str, str]] = []

        for idx, obj in enumerate(archive.objects):
            class_name = archive.class_names[obj.class_name_index].name
            if class_name != "NSString":
                continue
            value_slice = archive.values[obj.values_index:obj.values_index + obj.value_count]
            for value in value_slice:
                key_name = archive.keys[value.key_index].name
                if key_name != "NS.bytes" or value.type_code != TYPE_DATA or not isinstance(value.data, bytes):
                    continue
                try:
                    source = value.data.decode("utf-8")
                except UnicodeDecodeError:
                    continue
                target = replacements.get(source)
                if not target or target == source:
                    continue
                value.data = target.encode("utf-8")
                changed.append((idx, source, target))

        if changed:
            path.write_bytes(serialize_archive(archive))
        return changed

    def apply_to_app(self, app_path: str | Path) -> dict[str, list[tuple[int, str, str]]]:
        app_path = Path(app_path).expanduser().resolve()
        resources = app_path / "Contents" / "Resources"
        results: dict[str, list[tuple[int, str, str]]] = {}

        for relative_path, replacements in self.patches.items():
            target = resources / relative_path
            if not target.exists():
                continue
            changed = self.patch_archive_file(target, replacements)
            if changed:
                results[relative_path] = changed

        return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Patch compiled nib strings for VOCALOID6")
    parser.add_argument("--app-path", required=True, help="target VOCALOID6 .app path")
    parser.add_argument("--lang", default="zh-TW", help="language code")
    parser.add_argument("--config", help="custom compiled nib patch config")
    args = parser.parse_args()

    patcher = CompiledNibPatcher(language=args.lang, config_path=args.config)
    results = patcher.apply_to_app(args.app_path)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
