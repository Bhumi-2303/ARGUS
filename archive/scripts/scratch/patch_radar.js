const fs = require('fs');

let code = fs.readFileSync('web/src/features/benchmark/ModelComparisonPage.tsx', 'utf-8');

code = code.replace(/value: \[\s*r\.MCC \?\? 0,\s*r\.F1 \?\? 0,\s*r\.Specificity \?\? \(1 - \(\(1 - \(r\.Specificity \?\? 1\)\) \?\? 0\)\),\s*r\.Recall \?\? 0,\s*1 - \(\(1 - \(r\.Specificity \?\? 1\)\) \?\? 0\),\s*\]/m, 
`value: [
              r.MCC ?? 0,
              r.F1 ?? 0,
              r.Specificity ?? 0,
              r.Recall ?? 0,
              r.Accuracy ?? 0,
            ]`);

// Wait, looking at indicator:
code = code.replace(/{ name: '1 - FPR', max: 1 },/, "{ name: 'Accuracy', max: 1 },");

fs.writeFileSync('web/src/features/benchmark/ModelComparisonPage.tsx', code);
