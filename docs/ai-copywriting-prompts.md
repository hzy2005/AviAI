# AI Copywriting Prompt Versions

## Scope
- Endpoint: `POST /api/v1/posts/ai-copywriting`
- Modes: `generate`, `polish`
- Goal: keep prompt evolution explicit and regression-testable.

## Version History

### v1.0 (initial)
- `generate`: generic text prompt with weak image grounding.
- `polish`: simple rewrite prompt.
- Known risks: empty style control, unstable output structure.

### v1.1 (bird grounding)
- `generate` prompt includes bird recognition hint (`birdName`, `confidence`).
- Adds species mention guard to reduce “image-unrelated” copy.

### v1.2 (vision-capable generation)
- `generate` prefers vision-capable model call (`text + image_url`).
- Falls back to text model when vision path fails.

### v1.3 (structured generate prompt)
- `generate` enforces 3-sentence structure:
  - scene sentence
  - observation sentence
  - feeling sentence
- Length target: `50-90` Chinese characters.
- Disallows vague template phrases and markdown-like output.

### v1.4 (strict polish rules)
- `polish` requires:
  - preserve original meaning
  - do not add new facts (person/time/place/event)
  - improve fluency/readability/emotional tension
  - plain text only

### v1.5 (dual polish variants)
- `polish` returns:
  - `lite`
  - `enhanced`
  - `defaultVariant=lite`
- `content` remains compatible and equals `lite`.

### v1.6 (quality gate + one retry)
- Adds post-check gate for AI outputs:
  - non-empty
  - minimum length
  - no repeated fragments
  - no banned template phrase
- If first attempt fails quality gate, retries once before fallback.

### v1.7 (observability + tunable params)
- Response includes `aiMeta`:
  - `mode`
  - `model`
  - `elapsedMs`
  - `retryCount`
  - `fallback`
  - `params` (temperature/maxTokens)
- Configurable params:
  - `DEEPSEEK_TEXT_TEMPERATURE`
  - `DEEPSEEK_TEXT_MAX_TOKENS`
  - `DEEPSEEK_VISION_TEMPERATURE`
  - `DEEPSEEK_VISION_MAX_TOKENS`

## Regression Checklist
- Generate contract:
  - has `mode/content/source/aiMeta`
  - content follows 3-sentence structure and length band
- Polish contract:
  - has `content/lite/enhanced/defaultVariant/sources/aiMeta`
  - `content == lite`
- Fallback behavior:
  - when quality check fails after retry, response still returns usable fallback text.

## Notes for Future Prompt Changes
- Always update this file when changing prompt templates or quality rules.
- Keep tests synchronized in `backend/tests/test_ai_copywriting_regression.py`.
