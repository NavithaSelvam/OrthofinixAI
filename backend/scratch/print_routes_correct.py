from app.main import app
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from starlette.routing import Mount

for route in app.routes:
    if isinstance(route, APIRoute):
        print(f"PATH: {route.path} | METHODS: {route.methods} | NAME: {route.name}")
    elif isinstance(route, Mount):
        print(f"MOUNT: {route.path} | NAME: {route.name}")
    else:
        print(f"ROUTE: {route.path} | NAME: {route.name}")
