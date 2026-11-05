import re

with open("web/src/components/AppShell.tsx", "r") as f:
    code = f.read()

imports = """import { Skeleton } from './Skeleton';
import { Footer } from './Footer';
import { clsx } from 'clsx';"""
code = code.replace("import { Skeleton } from './Skeleton';\nimport { clsx } from 'clsx';", imports)

# Adjust bg colors
code = code.replace('className="min-h-screen bg-slate-950 text-slate-100 flex flex-col antialiased"', 
                    'className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col antialiased"')

# Add Footer
footer_injection = """              {children}
            </Suspense>
          </ErrorBoundary>
        </div>
        <Footer />
      </main>"""
code = code.replace("""              {children}
            </Suspense>
          </ErrorBoundary>
        </div>
      </main>""", footer_injection)

with open("web/src/components/AppShell.tsx", "w") as f:
    f.write(code)
