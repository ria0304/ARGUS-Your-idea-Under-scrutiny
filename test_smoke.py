"""Smoke test for ARGUS API endpoints."""

import pytest
import httpx
import asyncio
from apps.api.main import app

@pytest.mark.asyncio
async def test_root_endpoint():
    """Test the root endpoint returns service info."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "ARGUS AI Research & Decision Intelligence Agent"
        assert data["version"] == "1.0.0"
        assert data["status"] == "operational"

@pytest.mark.asyncio
async def test_health_endpoint():
    """Test the health check endpoint."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

@pytest.mark.asyncio
async def test_investigate_endpoint():
    """Test the investigate endpoint (will use stub agents)."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=30.0) as client:
        response = await client.post(
            "/investigate",
            json={
                "idea": "An efficient multimodal model for misinformation detection",
                "mode": "investigate",
                "use_tavily": False,
                "create_project": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "complete"
        assert "investigation_id" in data
        assert "data" in data

@pytest.mark.asyncio
async def test_break_it_endpoint():
    """Test the break-it endpoint."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=30.0) as client:
        response = await client.post(
            "/break-it",
            json={
                "idea": "An efficient multimodal model for misinformation detection",
                "mode": "break",
                "use_tavily": False,
                "create_project": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "complete"
        assert data["mode"] == "break"
        assert "data" in data

@pytest.mark.asyncio
async def test_mirror_endpoint():
    """Test the mirror endpoint."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=30.0) as client:
        response = await client.post(
            "/mirror",
            json={
                "idea": "An efficient multimodal model for misinformation detection",
                "mode": "mirror",
                "use_tavily": False,
                "create_project": False
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "complete"
        assert data["mode"] == "mirror"
        assert "data" in data

@pytest.mark.asyncio
async def test_dashboard_endpoint():
    """Test the dashboard endpoint."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "novelty" in data
        assert "evidence" in data
        assert "feasibility" in data
        assert "impact" in data
        assert "gap" in data
        assert "breakpoint" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])