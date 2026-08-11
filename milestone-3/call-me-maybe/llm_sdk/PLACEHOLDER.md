# llm_sdk/ (placeholder)

Este directorio debe contener el paquete `llm_sdk` proporcionado por 42
(con el wrapper `Small_LLM_Model`), copiado tal cual junto a `src/`, como
indica la Sec. IV.3.1 del enunciado.

No se incluye aqui porque es material distribuido por la escuela, no
generado por este proyecto. Sustituye este archivo por el contenido real
de `llm_sdk/` antes de ejecutar `uv run python -m src`.

Interfaz que `src/generator.py` y `src/vocabulary.py` esperan encontrar en
`llm_sdk.Small_LLM_Model` (ver Sec. V.3.1 del enunciado):

- `get_logits_from_input_ids(input_ids) -> Tensor`
- `get_path_to_vocabulary_json() -> str`
- `encode(text: str) -> list[int]`
- `decode(token_ids: list[int]) -> str` (opcional, se usa si esta disponible)
