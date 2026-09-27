const fs = require('fs');

let code = fs.readFileSync('web/src/features/overview/OverviewPage.tsx', 'utf-8');

code = code.replace(
`<span className="text-rose-400 font-bold flex items-center gap-1 text-xs mt-1">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      DRIFT DETECTED
                    </span>`,
`{shiftData?.domain_shift ? (
                    <span className="text-rose-400 font-bold flex items-center gap-1 text-xs mt-1">
                      <AlertTriangle className="w-3.5 h-3.5" />
                      DRIFT DETECTED
                    </span>
                  ) : (
                    <span className="text-emerald-400 font-bold flex items-center gap-1 text-xs mt-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      STABLE
                    </span>
                  )}`
);

// We need to make sure CheckCircle2 is imported if we use it, otherwise we can use ShieldCheck or just text.
// Let's check imports
if (!code.includes('CheckCircle2')) {
    code = code.replace(/import {([^}]*)AlertTriangle/g, 'import {$1AlertTriangle, CheckCircle2');
}

fs.writeFileSync('web/src/features/overview/OverviewPage.tsx', code);
