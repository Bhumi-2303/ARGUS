import re

with open("web/src/App.tsx", "r") as f:
    code = f.read()

imports = """import { PAGES } from './app/pages';
import PrivacyPolicyPage from './features/legal/PrivacyPolicyPage';
import TermsPage from './features/legal/TermsPage';
"""

code = code.replace("import { PAGES } from './app/pages';", imports)

routes = """              {PAGES.map((page) => {
                const PageComponent = page.component;
                return (
                  <Route
                    key={page.id}
                    path={page.path}
                    element={<PageComponent />}
                  />
                );
              })}
              <Route path="/privacy" element={<PrivacyPolicyPage />} />
              <Route path="/terms" element={<TermsPage />} />"""

code = code.replace("""              {PAGES.map((page) => {
                const PageComponent = page.component;
                return (
                  <Route
                    key={page.id}
                    path={page.path}
                    element={<PageComponent />}
                  />
                );
              })}""", routes)

with open("web/src/App.tsx", "w") as f:
    f.write(code)
