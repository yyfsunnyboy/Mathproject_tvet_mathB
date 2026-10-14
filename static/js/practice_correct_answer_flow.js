(function (global) {
  "use strict";

  const SUCCESS_MESSAGES = Object.freeze([
    "🎉 答對了！很棒！讓我們繼續下一題吧！",
    "答對了！保持這個節奏！",
    "答對了！做得好，你離目標又近了一步！",
  ]);

  function pickSuccessMessage(randomValue) {
    const value = Number.isFinite(randomValue) ? randomValue : Math.random();
    const index = Math.min(
      SUCCESS_MESSAGES.length - 1,
      Math.max(0, Math.floor(value * SUCCESS_MESSAGES.length)),
    );
    return SUCCESS_MESSAGES[index];
  }

  async function handleCorrectAnswer(options) {
    const config = options || {};
    if (typeof config.confirmMessage !== "function") {
      throw new TypeError("confirmMessage is required");
    }

    const message = pickSuccessMessage(config.randomValue);
    await config.confirmMessage(message);
    if (typeof config.onConfirm === "function") {
      return config.onConfirm();
    }
    return undefined;
  }

  global.PracticeCorrectAnswerFlow = Object.freeze({
    SUCCESS_MESSAGES,
    pickSuccessMessage,
    handleCorrectAnswer,
  });
})(window);
