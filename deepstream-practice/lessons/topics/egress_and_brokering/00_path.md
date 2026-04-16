# Egress And Brokering Topic

Day la topic cho output split va message brokering:

- `apps/deepstream-test4`

## What this topic teaches

- `nvmsgconv`
- `nvmsgbroker`
- `tee` for split output
- Event message meta
- Payload schema selection
- Protocol adaptor configuration

## Suggested lesson order

1. `./01_event_msg_pipeline/01_guide.md`
2. `./01_event_msg_pipeline/02_coding_guide.md`
3. `./01_event_msg_pipeline/03_starter.py`
4. `./01_event_msg_pipeline/04_extensions.md`
5. `./01_event_msg_pipeline/05_reference.py`
6. `./02_schema_and_adaptor_config/01_guide.md`
7. `./02_schema_and_adaptor_config/02_coding_guide.md`
8. `./02_schema_and_adaptor_config/03_starter.py`
9. `./02_schema_and_adaptor_config/04_extensions.md`
10. `./02_schema_and_adaptor_config/05_reference.py`

## Boundary

- Khong day sang tracker hay imagedata neu khong can thiet cho egress.
- Tang trong so cho output pipeline, networking, va config-driven deployment.
- Lesson 01 tap trung vao pipeline split + event msg attach.
- Lesson 02 tap trung vao schema type + adaptor config + broker options.
