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

The existing routes are `/api/practice/ai-check-handwriting`, `/analyze_handwriting`, and `/chat_ai`. The standard practice template is `templates/index.html`; adaptive practice uses `templates/adaptive_practice_v2.html`. The handwriting check is recognition and tutoring only. The official grading flow remains `/check_answer`.

## Verification

Test three turns on one question, a changed canvas, next-question isolation, distinct users, duplicate submissions, and delayed responses. Cover representative supported question shapes in each school system. Use automated and API tests, then live browser acceptance against a runtime with a reachable AI model. Mark live AI unverified if that call cannot be observed.
