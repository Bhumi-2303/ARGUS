const fs = require('fs');

let code = fs.readFileSync('web/src/features/benchmark/ModelComparisonPage.tsx', 'utf-8');

// Replace lowercase API mappings with proper CSV capitalization
code = code.replace(/r\.mcc/g, 'r.MCC');
code = code.replace(/dRow\.mcc/g, 'dRow.MCC');

code = code.replace(/r\.f1_score/g, 'r.F1');
code = code.replace(/dRow\.f1_score/g, 'dRow.F1');

code = code.replace(/r\.accuracy/g, 'r.Accuracy');
code = code.replace(/r\.recall/g, 'r.Recall');
code = code.replace(/r\.specificity/g, 'r.Specificity');

// For FPR: Replace `typeof r.fpr === 'number' ? r.fpr.toFixed(4) : '-'`
code = code.replace(/typeof r\.fpr === 'number' \? r\.fpr\.toFixed\(4\) : '-'/g, 
  "typeof r.Specificity === 'number' ? (1 - r.Specificity).toFixed(4) : '-'");

code = code.replace(/typeof dRow\.fpr === 'number' \? dRow\.fpr\.toFixed\(4\) : '-'/g, 
  "typeof dRow.Specificity === 'number' ? (1 - dRow.Specificity).toFixed(4) : '-'");

code = code.replace(/r\.fpr \?\? 0\.05/g, "(1 - (r.Specificity ?? 1))");

code = code.replace(/r\.threshold/g, 'r.Threshold');

// Fix radar chart:
// r.mcc ?? 0 -> r.MCC ?? 0
// r.f1_score ?? 0 -> r.F1 ?? 0
// r.specificity ?? (1 - (r.fpr ?? 0)) -> r.Specificity ?? 0
// r.recall ?? 0 -> r.Recall ?? 0
// r.accuracy ?? 0 -> r.Accuracy ?? 0
code = code.replace(/r\.fpr/g, '(1 - (r.Specificity ?? 1))');

fs.writeFileSync('web/src/features/benchmark/ModelComparisonPage.tsx', code);
