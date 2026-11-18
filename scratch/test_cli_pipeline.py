"""
Test Suite for Antigravity CLI Pipeline Endpoints
"""
import sys
import pathlib

# Ensure workspace root is in python path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
import backend.main as main
import backend.antigravity_cli as cli

client = TestClient(main.app)

def test_endpoints():
    print("1. Testing task-status endpoint...")
    res = client.get("/api/episodes/ep01-sample/task-status")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    print("   ✓ task-status:", data["status"], "total_scenes:", data["total_scenes"])

    print("2. Testing project alias task-status...")
    res = client.get("/api/projects/ep01-sample/task-status")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    print("   ✓ alias task-status ok")

    print("3. Testing CLI command resolution...")
    cmd = cli.get_cli_command()
    print("   ✓ Resolved CLI Command:", cmd)
    assert len(cmd) > 0, "No CLI command resolved"

    print("ALL ENDPOINT CHECKS PASSED!")

if __name__ == "__main__":
    test_endpoints()
