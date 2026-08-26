from app.main import app

for route in app.routes:
    print(f"PATH: {route.path} | METHODS: {route.methods} | NAME: {route.name}")
