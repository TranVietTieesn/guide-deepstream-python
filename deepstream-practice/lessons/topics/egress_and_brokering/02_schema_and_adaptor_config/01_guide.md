# Lesson 02: Schema and Adaptor Config

Lesson nay di sau pipeline basics va tap trung vao config-driven egress:

- payload schema
- connection string
- adaptor cfg file
- backend choice

## What You Will Build

- Data path:
  same as lesson 01
- Input: same file input
- Output: giu pipeline nhu cu, nhung thay doi backend schema/config behavior

## Why It Matters

Trong production, egress khong chi la "gui message":

- ban phai chon schema phu hop
- ban phai truyen dung adaptor library
- ban phai biet backend nao can cfg file hay conn string

Lesson nay giup ban biet deployment knobs co y nghia gi.

## Compared to Lesson 01

Phan giu nguyen:

- event msg meta generation
- tee split
- `nvmsgconv`
- `nvmsgbroker`

Phan moi:

- schema type selection
- adaptor backend variants
- config file contracts
- broker specific connection rules

## New Concepts In This Lesson

### Schema type

- Full schema va minimal schema co format khac nhau.
- `payload-type` thay doi payload converter behavior.

### Protocol adaptor

- `nvmsgbroker` khong gui truc tiep ma qua protocol library.
- Moi backend co lib, conn string, va config nuances rieng.

### Config contract

- Mot so backend can ca cfg file va conn string.
- Mot so backend chi can conn string hoac topic.

## Mental Model

### Control flow

- App chi dinh what to send.
- Config chi dinh how to send.
- Broker adaptor chi dinh where to send.

### Deployment model

- `proto-lib` la runtime plugin.
- `cfg-file` la policy/config layer.
- `conn-str` la connection target.

## Implementation Checklist

1. Doc `--proto-lib`.
2. Doc `--conn-str`.
3. Doc `--cfg-file`.
4. Doc `--schema-type`.
5. Doc `--topic`.
6. Set corresponding properties on msgbroker/msgconv.
7. Run with no-display and display modes.

## Common Failure Modes

- Schema type khong khop voi partition/topic expectation.
- `proto-lib` sai path.
- Config file thieu `[message-broker]`.
- Chon backend nhung khong cap dung optional cfg.
- Quen match topic trong connection string va CLI.

## Self-Check

- `payload-type` thay doi gi trong converter?
- `proto-lib` co phai la backend server khong?
- Khi nao can `cfg-file`?
- Vi sao lesson nay la config-driven deployment lab?

## Extensions

- Thu mot backend khac neu moi truong co san.
- Doi schema type va quan sat payload behavior.
- Chay voi `--no-display`.
