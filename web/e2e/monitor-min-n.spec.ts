import { test, expect } from '@playwright/test';

test.describe('Live Monitor Minimum-N Rendering', () => {
  test('Metric cards show warming up state and require denominator until min-n is met', async ({ page }) => {
    // Intercept domain/model APIs to return simple data so the page loads cleanly
    await page.route('**/api/v1/domains', route => route.fulfill({
      status: 200,
      json: { domains: [{ domain_id: 'nfton', name: 'NF-ToN-IoT-v2', status: 'verified', sample_count: 100 }] }
    }));
    await page.route('**/api/v1/models', route => route.fulfill({
      status: 200,
      json: { models: [{ model_id: 'model_d2_coral', name: 'Clean Class-Aware CORAL', status: 'verified', protocol_status: 'coral_aligned', threshold: 0.5 }] }
    }));

    await page.goto('/monitor');
    
    // Check initial state (n=0)
    await expect(page.getByText('WARMING UP')).toBeVisible();
    await expect(page.getByText('Requires 50 total events')).toBeVisible();

    // Mock EventSource to simulate streaming events precisely
    await page.evaluate(() => {
      // Create a fake EventSource class
      class FakeEventSource {
        onmessage: any;
        constructor(url: string) {
          (window as any).fakeEventSourceInstance = this;
        }
        close() {}
      }
      (window as any).EventSource = FakeEventSource;
    });

    // Start stream
    await page.getByRole('button', { name: /Start Stream/i }).click();

    // Fire 1 event
    await page.evaluate(() => {
      const instance = (window as any).fakeEventSourceInstance;
      instance.onmessage({
        data: JSON.stringify({
          id: "1",
          timestamp: new Date().toISOString(),
          domain: "nfton",
          features: {},
          true_label: 1, // Attack
          predictions: { "model_d2_coral": { label: 1, probability: 0.99 } }
        })
      });
    });

    // We fired 1 event (Attack, TP). 
    // n=1 total, 1 attack / 0 benign.
    // It should still say WARMING UP.
    await expect(page.getByText('WARMING UP')).toBeVisible();
    await expect(page.getByText('(n=1, 1 atk / 0 ben)')).toBeVisible();
    
    // The metric itself should NOT just be a percentage. It should be pulsed out "--.-%"
    // Since we used `animate-pulse` and `--.-%` in the UI:
    const placeholders = await page.locator('.animate-pulse').count();
    expect(placeholders).toBeGreaterThan(0);

    // Fire 49 more events to cross the MIN_TOTAL_N=50 and MIN_CLASS_N=5 threshold
    // Let's fire 5 benign (TN) and 44 attack (TP)
    await page.evaluate(() => {
      const instance = (window as any).fakeEventSourceInstance;
      for (let i=0; i<5; i++) {
        instance.onmessage({
          data: JSON.stringify({
            id: "b"+i, timestamp: new Date().toISOString(), domain: "nfton", features: {},
            true_label: 0, predictions: { "model_d2_coral": { label: 0, probability: 0.1 } }
          })
        });
      }
      for (let i=0; i<44; i++) {
        instance.onmessage({
          data: JSON.stringify({
            id: "a"+i, timestamp: new Date().toISOString(), domain: "nfton", features: {},
            true_label: 1, predictions: { "model_d2_coral": { label: 1, probability: 0.9 } }
          })
        });
      }
    });

    // Now n=50 total, 45 attack / 5 benign.
    // WARMING UP should disappear.
    await expect(page.getByText('WARMING UP')).not.toBeVisible();
    
    // Should show real percentage and the denominator text
    await expect(page.getByText('100.0%')).toBeVisible();
    await expect(page.getByText('(n=50, 45 atk / 5 ben)')).toBeVisible();
  });
});
