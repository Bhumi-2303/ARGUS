import re
import os

def patch_file(filepath, replacements):
    with open(filepath, "r") as f:
        code = f.read()
    for old, new in replacements:
        code = code.replace(old, new)
    with open(filepath, "w") as f:
        f.write(code)

patch_file("web/src/features/overview/OverviewPage.tsx", [
    ('<div className="absolute top-0 right-0 -mt-10 -mr-10 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />', ''),
    ('rounded-full bg-cyan-500/10', 'rounded bg-cyan-500/10'),
    ('group hover:border-emerald-500/50 transition-all duration-300', ''),
    ('group hover:border-rose-500/50 transition-all duration-300', ''),
    ('group-hover:text-amber-300 transition-colors', ''),
    ('group-hover:text-emerald-300 transition-colors', ''),
    ('group-hover:text-rose-300 transition-colors', '')
])

patch_file("web/src/components/TopBar.tsx", [
    ('rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300', 'rounded bg-blue-500/10 border border-blue-500/30 text-blue-700 dark:text-blue-300'),
    ('Made with AI', 'ARGUS Platform')
])

patch_file("web/src/features/placeholder/PlaceholderPage.tsx", [
    ('rounded-full', 'rounded')
])

patch_file("web/src/components/EmptyState.tsx", [
    ('rounded-full', 'rounded-md')
])

patch_file("web/src/components/StatusPill.tsx", [
    ('rounded-full border', 'rounded-sm border')
])

patch_file("web/src/components/ProvenanceBadge.tsx", [
    ('rounded-full', 'rounded-sm')
])
