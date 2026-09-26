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
        if (typeof globalThis !== 'undefined' && globalThis.MathDisplayNormalizer) {
            const normalized = globalThis.MathDisplayNormalizer.normalizeMathText(canonical, { mathContext: true });
            if (normalized !== canonical) return normalized;
        }
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

        // Bare TeX atoms (e.g. \overrightarrow{AB}, \vec{a}) must be delimited.
        if (/\\[a-zA-Z]+/.test(canonical) && !/(?:\\\(|\\\[|\$\$|\$)/.test(canonical)) {
            return `\\(${canonical}\\)`;
        }

        // Classroom equations / powers (same contract as stem MathJax).
        const hasCJK = /[\u4e00-\u9fff]/.test(canonical);
        const looksEquation = !hasCJK && ((/=/.test(canonical) && /[xyXY]/.test(canonical))
            || (/\^/.test(canonical) && /[A-Za-z]/.test(canonical))
            || /π|(?<![A-Za-z])pi(?![A-Za-z])/i.test(canonical));
        if (looksEquation && !/(?:\\\(|\\\[|\$\$|\$)/.test(canonical)) {
            let latex = canonical.replace(/π/g, '\\pi').replace(/\bpi\b/gi, '\\pi');
            latex = latex.replace(/([A-Za-z0-9\)])\^(\{[^}]+\}|[A-Za-z0-9]+)/g, (_, base, exp) => {
                const body = String(exp).replace(/^\{|\}$/g, '');
                return `${base}^{${body}}`;
            });
            return `\\(${latex}\\)`;
        }

        return canonical;
    }

    function choiceDisplay(choice) {
        if (choice && typeof choice === 'object' && choice.display) {
            return formatChoiceMathDisplay(choice.display);
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
