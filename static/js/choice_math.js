(function (root, factory) {
    const api = factory();
    if (typeof module === 'object' && module.exports) {
        module.exports = api;
    }
    if (root) {
        root.ChoiceMathRuntime = api;
    }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
    'use strict';

    function formatChoiceMathDisplay(value) {
        const canonical = String(value || '').trim();
        if (!canonical) return canonical;
        if (/^[+-]?\d+(?:\.\d+)?$/.test(canonical)) return canonical;
        if (/^\(\s*[+-]?\d+(?:\.\d+)?(?:\/\d+)?\s*,\s*[+-]?\d+(?:\.\d+)?(?:\/\d+)?\s*\)$/.test(canonical)) {
            return canonical;
        }

        let match = canonical.match(/^([+-]?\d+)\*sqrt\(([^()]+)\)\/(\d+)$/);
        if (match) return `\\(\\frac{${match[1]}\\sqrt{${match[2]}}}{${match[3]}}\\)`;

        match = canonical.match(/^([+-]?\d+)\*sqrt\(([^()]+)\)$/);
        if (match) return `\\(${match[1]}\\sqrt{${match[2]}}\\)`;

        match = canonical.match(/^sqrt\(([^()]+)\)$/);
        if (match) return `\\(\\sqrt{${match[1]}}\\)`;

        match = canonical.match(/^([+-]?)(\d+)\/(\d+)$/);
        if (match) return `\\(${match[1]}\\frac{${match[2]}}{${match[3]}}\\)`;

        return canonical;
    }

    function choiceDisplay(choice) {
        if (choice && typeof choice === 'object' && choice.display) {
            return String(choice.display);
        }
        if (choice && typeof choice === 'object') {
            return formatChoiceMathDisplay(choice.text || choice.value || '');
        }
        return formatChoiceMathDisplay(choice);
    }

    return {
        choiceDisplay: choiceDisplay,
        formatChoiceMathDisplay: formatChoiceMathDisplay
    };
}));
