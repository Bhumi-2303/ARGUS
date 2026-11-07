with open("src/argus/api/main.py", "r") as f:
    code = f.read()

if "from argus.api.routers import data" not in code:
    code = code.replace("from argus.api.routers import health, agents", "from argus.api.routers import health, agents, data")
    code = code.replace('api_router.include_router(agents.router, prefix="/agents")', 'api_router.include_router(agents.router, prefix="/agents")\napi_router.include_router(data.router, prefix="/data")')
    with open("src/argus/api/main.py", "w") as f:
        f.write(code)
