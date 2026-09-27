import re
with open("web/src/app/pages.ts", "r") as f:
    content = f.read()

content = content.replace(
    "const InteractiveDemoPage = lazy(() => import('../features/demo/InteractiveDemoPage'));",
    "const InteractiveDemoPage = lazy(() => import('../features/demo/InteractiveDemoPage'));\nconst JudgeModePage = lazy(() => import('../features/demo/JudgeModePage'));"
)

new_page = """  {
    id: 'judge',
    path: '/judge-mode',
    title: 'Judge Mode',
    description: 'Automated end-to-end scenario replay of domain adaptation.',
    category: 'Overview',
    icon: Play,
    component: JudgeModePage,
    badge: 'AUTO',
  },
  {
    id: 'demo',"""

content = content.replace("  {\n    id: 'demo',", new_page)

with open("web/src/app/pages.ts", "w") as f:
    f.write(content)
