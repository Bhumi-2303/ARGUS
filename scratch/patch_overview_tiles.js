const fs = require('fs');

let code = fs.readFileSync('web/src/features/overview/OverviewPage.tsx', 'utf-8');

// First, we need to extract the Source-only XGBoost model as well.
// We look for where dannModel, coralModel, sourceModel are defined.
const searchStr = `  const sourceModel = benchmarkRows.find((r: any) => r.Model?.includes('Global CORAL')) || null;`;
const insertStr = `  const sourceModel = benchmarkRows.find((r: any) => r.Model?.includes('Global CORAL')) || null;
  const sourceOnlyModel = benchmarkRows.find((r: any) => r.Model?.includes('Source-only XGBoost')) || null;
`;

code = code.replace(searchStr, insertStr);

// Then replace the tile
const oldTile = `                  <div>
                    <span className="text-slate-400 block text-[10px]">Source MCC (Baseline)</span>
                    <span className="text-emerald-400 text-lg font-extrabold">
                      {typeof dannMCC === 'number' ? dannMCC.toFixed(4) : '-'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">Unadapted Target MCC</span>
                    <span className="text-rose-400 text-lg font-extrabold">
                      {typeof sourceModel?.target_mcc === 'number' ? sourceModel.target_mcc.toFixed(4) : '-'}
                    </span>
                  </div>`;

// Or if it was using the hardcoded one (just in case I replaced it globally before)
// Let's just use regex to replace the two divs in that grid.

const newTile = `                  <div>
                    <span className="text-slate-400 block text-[10px]">Unadapted Target MCC</span>
                    <span className="text-rose-400 text-lg font-extrabold">
                      {typeof sourceOnlyModel?.MCC === 'number' ? sourceOnlyModel.MCC.toFixed(4) : '-'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">Adapted Target MCC</span>
                    <span className="text-emerald-400 text-lg font-extrabold">
                      {typeof coralMCC === 'number' ? coralMCC.toFixed(4) : '-'}
                    </span>
                  </div>`;

// Wait, the title of the card is:
// 1. In-Domain vs. Cross-Domain Drop
// The prompt says "In-Domain vs. Cross-Domain Drop tile shows numbers (Source MCC 0.0129 / Unadapted Target MCC 0.7203) that don't match any real metric pairing... Fix so this tile shows a real, correctly-labeled pairing (e.g. actual Source-only XGBoost MCC of -0.031074 vs. whatever the intended comparison metric actually is)".
// If we name them "Unadapted Target MCC" and "Adapted Target MCC", we should probably change the title of the card to match, or change the text.
// Or we can leave the title and just show the comparison. "Unadapted Target MCC" (-0.0310) vs "Adapted Target MCC" (0.3855).

code = code.replace(/<span className="text-slate-400 block text-\[10px\]">Source MCC \(Baseline\)<\/span>[\s\S]*?(?=<\/div>\s*<\/div>\s*<\/div>\s*\)} )/, newTile + '\n                ');

// Wait! If I change the tile from "Source MCC (Baseline)" and "Unadapted Target MCC" to "Unadapted Target MCC" and "Adapted Target MCC", I should also change the title.
code = code.replace(
  '1. In-Domain vs. Cross-Domain Drop',
  '1. Unadapted vs. Adapted Cross-Domain Performance'
);

fs.writeFileSync('web/src/features/overview/OverviewPage.tsx', code);
