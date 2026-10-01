import re
import codecs

with codecs.open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace block 1:
# if (data.answer_type === 'handwriting') { ... } else { ... }
# We match it using a regex without matching Chinese characters literally.
regex1 = r"(// [^\n]*\n\s*if\s*\(data\.answer_type\s*===\s*'handwriting'\)\s*\{\s*answerInput\.disabled\s*=\s*true;\s*answerInput\.placeholder\s*=[^\n]*\s*submitBtn\.disabled\s*=\s*true;\s*\}\s*else\s*\{\s*answerInput\.disabled\s*=\s*false;\s*answerInput\.placeholder\s*=[^\n]*\s*submitBtn\.disabled\s*=\s*false;\s*\})"

replacement1 = """// 5. 調整輸入框狀態
                    window.currentGradingMode = data.grading_mode;
                    window.currentVariant = data.variant;
                    if (data.grading_mode === 'ai_judged_free_response') {
                        if (answerInput.tagName.toLowerCase() === 'input') {
                            const newTextarea = document.createElement('textarea');
                            newTextarea.id = 'answer-input';
                            newTextarea.className = answerInput.className;
                            newTextarea.style.flex = '1';
                            newTextarea.style.padding = '8px 12px';
                            newTextarea.style.fontSize = '0.95em';
                            newTextarea.style.border = '1px solid #ced4da';
                            newTextarea.style.borderRadius = '6px';
                            newTextarea.style.minHeight = '80px';
                            newTextarea.style.resize = 'vertical';
                            answerInput.parentNode.replaceChild(newTextarea, answerInput);
                            answerInput = newTextarea;
                        }
                        answerInput.disabled = false;
                        answerInput.placeholder = '請在此輸入完整的列舉過程與答案...';
                        submitBtn.disabled = false;
                    } else {
                        if (answerInput.tagName.toLowerCase() === 'textarea') {
                            const newInput = document.createElement('input');
                            newInput.type = 'text';
                            newInput.id = 'answer-input';
                            newInput.className = answerInput.className;
                            newInput.style.flex = '1';
                            newInput.style.padding = '8px 12px';
                            newInput.style.fontSize = '0.95em';
                            newInput.style.border = '1px solid #ced4da';
                            newInput.style.borderRadius = '6px';
                            answerInput.parentNode.replaceChild(newInput, answerInput);
                            answerInput = newInput;
                        }
                        if (data.answer_type === 'handwriting') {
                            answerInput.disabled = true;
                            answerInput.placeholder = '請在計算紙區域作答';
                            submitBtn.disabled = true;
                        } else {
                            answerInput.disabled = false;
                            answerInput.placeholder = '請在此輸入答案';
                            submitBtn.disabled = false;
                        }
                    }"""

if re.search(regex1, content):
    content = re.sub(regex1, replacement1, content, count=1)
    print("Replaced target1 successfully")
else:
    print("Regex 1 not found")

regex2 = r"(if\s*\(isProcessing\)\s*return;\s*isProcessing\s*=\s*true;\s*submitBtn\.disabled\s*=\s*true;\s*//[^\n]*\n\s*showLoadingMessage\(\);\s*fetch\('/check_answer',\s*\{)"

replacement2 = """if (isProcessing) return;
                isProcessing = true;
                submitBtn.disabled = true;

                // 顯示動態載入訊息
                showLoadingMessage();

                if (window.currentGradingMode === 'ai_judged_free_response') {
                    fetch('/api/free_response/tree_diagram/submit', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            answer_text: answerInput.value,
                            variant: window.currentVariant || "early_stopping_game"
                        })
                    })
                    .then(r => r.json())
                    .then(data => {
                        stopLoadingMessage();
                        if (!data.ok) {
                            resultDisplay.textContent = data.error || '提交失敗';
                            resultDisplay.className = 'incorrect';
                            return;
                        }
                        const r = data.result;
                        const isCorrect = r.status === 'correct';
                        resultDisplay.textContent = isCorrect ? '正確！' : (r.feedback || '部分正確或錯誤');
                        resultDisplay.className = isCorrect ? 'correct' : 'incorrect';
                        if (r.status === 'partial') resultDisplay.className = 'incorrect';

                        updateStreak(isCorrect);
                        if (isCorrect) {
                            handleCorrectAnswer();
                        }
                    })
                    .catch(err => {
                        stopLoadingMessage();
                        console.error('提交失敗:', err);
                        resultDisplay.textContent = '提交失敗';
                        resultDisplay.className = 'incorrect';
                    })
                    .finally(() => {
                        isProcessing = false;
                        submitBtn.disabled = false;
                    });
                    return;
                }

                fetch('/check_answer', {"""

if re.search(regex2, content):
    content = re.sub(regex2, replacement2, content, count=1)
    print("Replaced target2 successfully")
else:
    print("Regex 2 not found")

with codecs.open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
