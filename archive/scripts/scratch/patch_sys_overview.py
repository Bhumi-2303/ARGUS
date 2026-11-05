path = "web/src/features/system_overview/SystemOverviewPage.tsx"
with open(path, "r") as f:
    code = f.read()

# Currently: 
# const isHealthy = healthQuery.data?.status === 'healthy';
# status={isHealthy ? 'healthy' : healthError ? 'error' : 'connecting'}
# This logic is actually pretty safe because if it's undefined, it's not healthy.
# And if it fails (healthError), it shows error. If loading, it shows connecting.
# Wait, what if it returns status 'degraded' but no error? It would show 'connecting' because `isHealthy` is false, and `healthError` is false.
# Let's fix that.

code = code.replace("status={isHealthy ? 'healthy' : healthError ? 'error' : 'connecting'}", "status={isHealthy ? 'healthy' : healthError ? 'error' : healthQuery.data ? 'warning' : 'connecting'}")
code = code.replace("label={isHealthy ? 'Backend API Live' : healthError ? 'API Unreachable' : 'Connecting'}", "label={isHealthy ? 'Backend API Live' : healthError ? 'API Unreachable' : healthQuery.data ? 'Degraded / Unknown' : 'Connecting'}")

with open(path, "w") as f:
    f.write(code)
