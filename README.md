# AWS ECS Notes

Study notes and practical exercises for **Amazon ECS** (Elastic Container Service), in Markdown with Word (`.docx`) copies.

## Contents

| File | Description |
|---|---|
| [AWS_ECS_Complete_Notes.md](AWS_ECS_Complete_Notes.md) | Compute services overview, Lambda vs Fargate vs EC2 launch types, task and service management, connecting containers in a task, memory management, EC2 launch type infrastructure, and more |
| [AWS_ECS_Practical_Exercises.md](AWS_ECS_Practical_Exercises.md) | Hands-on exercises |
| `*.docx` | Word versions of both documents |
| `convert_to_word.py` | Regenerates the `.docx` files from the Markdown |

## Regenerate the Word files

```bash
pip install python-docx
python convert_to_word.py
```
