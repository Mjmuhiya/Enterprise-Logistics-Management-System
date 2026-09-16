from fastapi import FastAPI

app = FastAPI(
    title="LogiFlow Enterprise API",
    version="1.0.0",
    description="REST API for intelligent logistics and supply chain management.",
)


@app.get("/api/v1/health", tags=["System"])
def health_check() -> dict[str, str]:
    """Return service health for monitoring and smoke tests."""
    return {"status": "healthy", "service": "logiflow-api"}
