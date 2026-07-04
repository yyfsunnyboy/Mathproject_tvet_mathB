
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const base = process.argv[2];
  const question = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
  const expected = question.answer_contract.expected_answers || question.correct_answer;
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const submits = [];
  await page.route('**/api/adaptive/submit_and_get_next', async (route) => {
    const body = route.request().postDataJSON();
    submits.push(body);
    const isCorrect = body.user_answer
      && String(body.user_answer.x_intercept) === String(expected.x_intercept)
      && String(body.user_answer.y_intercept) === String(expected.y_intercept)
      && String(body.user_answer.function_equation) === String(expected.function_equation);
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        session_id: body.session_id || 'smoke-session',
        step_number: (body.step_number || 0) + 1,
        is_correct: isCorrect,
        completed: false,
        new_question_data: question,
        new_question_text: question.question_text || question.question || '',
      }),
    });
  });

  await page.goto(base + '/reports/frontend_smoke/page.html', { waitUntil: 'networkidle' });
  await page.waitForFunction(() => window.VisualSpecRuntime && typeof renderQuestion === 'function');

  await page.evaluate((payload) => {
    state.sessionId = 'smoke-session';
    state.stepNumber = 1;
    renderQuestion({
      session_id: 'smoke-session',
      step_number: 1,
      new_question_data: payload,
      new_question_text: payload.question_text || payload.question || '',
      question_uid: payload.question_uid || 'smoke-uid',
    });
  }, question);

  const ui = await page.evaluate(() => {
    const container = document.getElementById('questionVisualContainer');
    const canvas = document.getElementById('questionVisualCanvas');
    const fields = [...document.querySelectorAll('#multiPartAnswerFields [data-field-key]')].map((el) => el.dataset.fieldKey);
    const scratchpad = document.querySelector('.scratchpad-section');
    const answerInput = document.getElementById('answerInput');
    return {
      visualHidden: container.hidden,
      canvasW: canvas.width || canvas.clientWidth,
      canvasH: canvas.height || canvas.clientHeight,
      fieldKeys: fields,
      multiPartHidden: document.getElementById('multiPartAnswerFields').hidden,
      scratchpadDisplay: scratchpad ? scratchpad.style.display : null,
      singleInputDisplay: answerInput.style.display,
    };
  });

  if (ui.visualHidden) throw new Error('visual container hidden');
  if (!ui.canvasW || !ui.canvasH) throw new Error('canvas not sized');
  if (ui.fieldKeys.length !== 3) throw new Error('field count ' + ui.fieldKeys.length);
  const want = ['x_intercept', 'y_intercept', 'function_equation'];
  for (const k of want) if (!ui.fieldKeys.includes(k)) throw new Error('missing field ' + k);
  if (ui.multiPartHidden) throw new Error('multiPart hidden');
  if (ui.scratchpadDisplay !== 'none') throw new Error('drawing canvas visible: ' + ui.scratchpadDisplay);
  if (ui.singleInputDisplay !== 'none') throw new Error('single input still visible');

  async function fillAndSubmit(values) {
    for (const [key, value] of Object.entries(values)) {
      await page.fill('#multiPartAnswerFields [data-field-key="' + key + '"]', String(value));
    }
    await page.click('#submitBtn');
    await page.waitForTimeout(200);
  }

  await fillAndSubmit({
    x_intercept: expected.x_intercept,
    y_intercept: expected.y_intercept,
    function_equation: expected.function_equation,
  });
  await fillAndSubmit({
    x_intercept: '999',
    y_intercept: '999',
    function_equation: '999',
  });

  if (submits.length < 2) throw new Error('submit count ' + submits.length);
  for (const body of submits) {
    const ans = body.user_answer;
    if (!ans || typeof ans !== 'object' || Array.isArray(ans)) throw new Error('user_answer not object');
    for (const k of want) {
      if (!(k in ans)) throw new Error('missing submit key ' + k);
    }
  }
  const correctBody = submits[0].user_answer;
  const wrongBody = submits[1].user_answer;
  if (String(correctBody.x_intercept) !== String(expected.x_intercept)) throw new Error('correct payload mismatch');
  if (String(wrongBody.x_intercept) !== '999') throw new Error('wrong payload mismatch');

  console.log(JSON.stringify({
    ok: true,
    component: question.component_id || question.generator_key,
    fields: ui.fieldKeys,
    submits: submits.length,
    visualHidden: ui.visualHidden,
    scratchpadDisplay: ui.scratchpadDisplay,
  }));
  await browser.close();
})().catch((err) => {
  console.error(err && err.stack || err);
  process.exit(1);
});
