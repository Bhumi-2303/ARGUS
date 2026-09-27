with open("src/argus/api/main.py", "r") as f:
    code = f.read()

if "from argus.api.routers import data" not in code:
    code = code.replace("from argus.api.routers import health, domains", "from argus.api.routers import health, domains, data")
    code = code.replace('app.include_router(agents.router, prefix="/api/v1/agents")', 'app.include_router(agents.router, prefix="/api/v1/agents")\napp.include_router(data.router, prefix="/api/v1/data")')
    with open("src/argus/api/main.py", "w") as f:
        f.write(code)
