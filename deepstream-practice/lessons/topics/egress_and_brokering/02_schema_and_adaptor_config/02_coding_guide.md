# Lesson 02 Coding Guide

Lesson nay tap trung vao CLI/config va property wiring.

## Before You Code

- Input: file + broker options.
- Output: same pipeline, different backend behavior.
- Imports:
  - `OptionParser`
  - `pyds`
  - `PlatformInfo`

## Build Order

1. Giu nguyen event meta helpers.
2. Parse args va validate proto-lib/input.
3. Set broker properties.
4. Set msgconv schema properties.
5. Build same pipeline as lesson 01.
6. Link and run.

## Function-By-Function Walkthrough

### `parse_args()`

- Day la noi decide backend contract.
- Validate `proto_lib` va `input_file` la bat buoc.

### `main(args)`

- `msgconv.payload-type` map toi schema type.
- `msgbroker.config` va `msgbroker.topic` la optional knobs.
- `sink` co the la display hoac `fakesink`.

## Syntax Notes

- `parser.add_option("-s", "--schema-type", ...)`
  - full/minimal schema switch.
- `msgbroker.set_property("config", cfg_file)`
  - optional backend config.
- `msgbroker.set_property("topic", topic)`
  - topic override.

## Starter Mapping

- `TODO 1`: event meta helpers
- `TODO 2`: probe attach
- `TODO 3`: parse args
- `TODO 4`: pipeline construction
- `TODO 5`: tee and broker wiring

## Mini Checkpoints

- Schema type di vao cai gi?
- Config file di vao cai gi?
- Topic di vao cai gi?
- No-display co thay doi data path khong?
