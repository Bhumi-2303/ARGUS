import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from './context/ThemeContext';
import { AppShell } from './components/AppShell';
import { PAGES } from './app/pages';
import PrivacyPolicyPage from './features/legal/PrivacyPolicyPage';
import TermsPage from './features/legal/TermsPage';


const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5000,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <BrowserRouter>
          <AppShell>
            <Routes>
              {PAGES.map((page) => {
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
              <Route path="/terms" element={<TermsPage />} />
            </Routes>
          </AppShell>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
