# AI Tutor Conversation Contract

This contract applies to every practice page that already uses the shared AI Tutor, across junior high, general high school, and vocational B1–B4 skills. New skills inherit the shared routes and renderer; they must not create a skill-specific conversation service.

## Identity and authority

- A conversation belongs to the authenticated user (or the explicitly allowed guest demo session), practice session, and server-issued `question_uid`. The question store supplies `skill_id`, question text, and correct answer. The browser's identity, question text, answer, or conversation ID is never authority.
- Student tutoring routes reject an unknown, expired, cross-owner, or cross-session `question_uid`. `/chat_ai` and `/analyze_handwriting` require the UID; the recognition endpoint may instead accept an existing server-issued adaptive session ID that resolves one trusted question. A legacy path is allowed only when it resolves the same supplied UID through signed server session state. No route falls back to browser `correct_answer`, `expected_answer`, `question_text`, answer contracts, or special-question rubric fields.
- Tree-diagram and Pascal handwriting grading obtains its variant and expected paths, counts, rows, terms, or expansion only from the server-issued question metadata.
- A new question receives a new `question_uid`. History from another question or owner must not enter its model prompt.
- AI feedback never replaces the authoritative math checker or advances practice by itself.

## Turn data

The bounded server-side question store keeps ordered turns with role, kind, timestamp, and a concise content field. A handwriting turn also keeps the recognized mathematical steps, a SHA-256 image reference when available, assessment, reply, suggested questions, and submission ID. It does not keep image bytes or the correct answer in conversation history. Repeated submission IDs are not appended twice.

Before each AI call, the tutor includes the same question's recent turns, including prior student handwriting and AI replies. Keep at most `AI_CONVERSATION_MAX_TURNS` turns and trim each field to its configured bound. When the student writes again, append the new recognized work so the next turn can compare it with the earlier work.

The primary tutor client and legacy Gemini fallback must be stateless for each request. Never use a module-global model chat session as conversation memory; it can mix different students. The server-validated per-question turns are the only tutor memory.

## Response and UI

Every successful tutoring response exposes `reply` and exactly three `suggested_questions`. `follow_up_prompts` remains a compatibility alias. Prefer the model's distinct, contextual questions. If malformed or missing, derive three questions from the current question, recognized work, and current reply without another model request. A question must not reveal the final answer. A suggestion click sends a new `/chat_ai` message with the same `question_uid`; replace suggestions after the reply. Ignore a response whose captured question UID is no longer displayed.

The frontend renders any `reply` string as student text, including LaTeX with braces. It hides only a serialized schema object such as `{"reply": ...}`. When the model call fails or its output has no recoverable reply, `/chat_ai` returns HTTP 503 with `ai_unavailable: true` and `retryable: true`, and it records no turn. The page shows a temporary-failure message and lets the student resend the same question. It must not imply that the student asked unclearly.

The existing routes are `/api/practice/ai-check-handwriting`, `/analyze_handwriting`, and `/chat_ai`. The standard practice template is `templates/index.html`; adaptive practice uses `templates/adaptive_practice_v2.html`. The handwriting check is recognition and tutoring only. The official grading flow remains `/check_answer`.

## Pedagogical contract

`core/ai_tutor_pedagogy.py` holds the teaching rules for every tutor prompt (`/chat_ai` and the handwriting second stage). Do not copy these rules into skill-specific prompts.

- Verify the student's written lines first. Quote and confirm correct steps. Do not imply an error unless a specific line is shown to be wrong.
- The last-line comparison (`status`, `main_issue`, `error_mechanism`) cannot tell unfinished work from wrong work. Prompts label it as an unverified guess. The handwriting compliance check accepts "these steps are correct; next use this formula".
- Give a concrete next step: the formula or rule plus the substituted expression. A reply that only says "think again" or "check from the first step" is not acceptable.
- Answer formula, definition, and concept questions directly, then connect the answer to the current question and the student's work. Final-answer disclosure follows the teaching-round policy below.
- Each turn is classified as one intent: formula or definition, why a step, check my work, where I went wrong, next step, simpler explanation, full solution, or general. The prompt states that intent and its answering style.
- When recognition is uncertain, name the unclear symbol and ask about it. Never assume it is wrong.
- Suggested questions follow the current solving state: how to carry out the next step, what the formula used means, and how to check the step.
- A handwriting reply never says the answer is correct when the authoritative checker rejected the submission.

## Teaching rounds

`core/ai_tutor_pedagogy.py` defines one round policy for every skill (`TEACHING_ROUND_RULES`, `teaching_round_block`). Every tutor prompt includes the block. These are `/chat_ai`, its one-time rewrite, the handwriting second stage, and the tree-diagram and Pascal feedback. The block states that it overrides older "write the answer" wording in stored prompt templates.

- Round 1: diagnose the work, quote correct steps, and name the wrong number or symbol. Give the needed formula or direction and one small step. A formula or definition question still gets the general formula. Do not state the final answer.
- Round 2: build on round 1 and say what changed. Give a more concrete demonstration, such as a partial substitution. Leave at least one key step to the student. Do not state the final answer.
- Round 3 and later: give the full derivation and final answer only when the student explicitly asks (`full_solution` intent). Otherwise give the next step only.
- The student's own correct answer may always be affirmed.

The server alone computes the round. `current_teaching_round(question_uid)` returns the highest `teaching_round` recorded on that question's successful tutor turns, plus 1. The frontend never sends a round.

- Handwriting checks and text questions on the same question share the count.
- A 503, model failure, or recognition-incomplete reply records no round.
- A resent `handwriting_submission_id` keeps its original round and is not appended again.
- A new `question_uid`, another owner, or another practice session starts at round 1.
- Because the count is a maximum, not a tally, two concurrent requests in the same round cannot skip a round.
- The adaptive page does not persist its conversation, so it always stays at round 1. That is the strictest setting.

## Final-answer disclosure check

Before a reply is shown, `core/ai_tutor_disclosure.py` (`find_answer_disclosure`) compares its math with the server-side answer. It uses symbolic equivalence (SymPy), not string matching.

- Rearranged, scaled, or reduced forms count as disclosure: `3y=2x-15` for `y=\frac{2}{3}x-5`, `3/6` for `1/2`, and `3 \le x` for `x \ge 3`.
- General formulas (`y=mx+b`), partial substitutions (`\sqrt{1^2+7^2}`), and intermediate steps (`2x=8`) are not disclosure.
- A multi-part answer (`x=4 或 x=10`, coordinates, choices) is disclosed only when every part appears.
- Tree-diagram and Pascal rubrics count only when the full ordered row or path set appears.

When a round may not disclose the answer, `/chat_ai` first asks for one rewrite. If the rewrite still discloses, only the disclosing math is replaced with `（這一步留給你自己完成）`. The guard never substitutes different, mathematically wrong text. The same replacement applies to handwriting replies. Suggested questions that disclose the answer are dropped.

Capability boundary: proofs, constructions, drawings, and worded conclusions are matched only literally. A paraphrased proof or a described drawing cannot be detected automatically, so these rely on the prompt-level round policy.

## AI-check button

Both practice templates follow the same button contract:

- AI check is available whenever the question has a handwriting canvas (`handwriting_enabled` and `canvas_required` not false), or when `ai_check_required` is true. `ai_check_required: false` means optional, not blocked.
- Student ink on the canvas is enough; the answer text field is not required. Background grids and system figures are not ink. A blank canvas shows a message and sends no request.
- AI check is separate from formal submission. Recognition, `/check_answer`, and `/analyze_handwriting` each have a client timeout.
- An unfinished (`in_progress`) answer still gets a tutor reply on the current steps.
- Model or vision failures return HTTP 503 with `ai_unavailable` and `retryable`. They are not reported as unclear handwriting.
- Success and failure always end the loading state and re-enable the button. A failed check can be retried at once.
- Changing question cancels the pending check, resets the button, and clears the conversation. A late response for an old question is ignored.
- The browser sends only the student's work and the server-issued `question_uid`. It never sends a correct answer.

## Verification

Test three turns on one question, a changed canvas, next-question isolation, distinct users, duplicate submissions, and delayed responses. Cover representative supported question shapes in each school system. Use automated and API tests, then live browser acceptance against a runtime with a reachable AI model. Mark live AI unverified if that call cannot be observed.
