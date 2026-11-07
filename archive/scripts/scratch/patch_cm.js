const fs = require('fs');
let code = fs.readFileSync('web/src/features/benchmark/ModelComparisonPage.tsx', 'utf-8');

code = code.replace(/const tpPct = .*/, "const tpPct = typeof r.Recall === 'number' ? (r.Recall * 100).toFixed(0) : '-';");
code = code.replace(/const fpPct = .*/, "const fpPct = typeof r.Specificity === 'number' ? ((1 - r.Specificity) * 100).toFixed(0) : '-';");
code = code.replace(/const tnPct = .*/, "const tnPct = typeof r.Specificity === 'number' ? (r.Specificity * 100).toFixed(0) : '-';");
code = code.replace(/const fnPct = .*/, "const fnPct = typeof r.Recall === 'number' ? ((1 - r.Recall) * 100).toFixed(0) : '-';");

fs.writeFileSync('web/src/features/benchmark/ModelComparisonPage.tsx', code);
