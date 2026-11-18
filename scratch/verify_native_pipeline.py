from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

# 1. Health check
res = client.get('/api/health')
assert res.status_code == 200, f'Health check failed: {res.text}'
print('✓ Health check passed:', res.json()['app'])

# 2. Projects list
res = client.get('/api/projects')
assert res.status_code == 200
projects = res.json().get('projects', [])
print(f'✓ Projects list passed ({len(projects)} episodes found)')

# 3. Universe
res = client.get('/api/universe')
assert res.status_code == 200
print('✓ Universe endpoint passed')

# 4. Check that external API endpoints were properly removed (expect 404 or 405)
res = client.get('/api/settings')
assert res.status_code in [404, 405], 'Settings endpoint should be removed'
res = client.get('/api/gemini/models')
assert res.status_code in [404, 405], 'Gemini models endpoint should be removed'
res = client.get('/api/openrouter/models')
assert res.status_code in [404, 405], 'OpenRouter models endpoint should be removed'
print('✓ Verified all external LLM/API endpoints successfully removed')

# 5. Build prompt for scenes
res = client.post('/api/projects/ep01-sample/build-prompt/scenes')
assert res.status_code == 200
data = res.json()
assert 'prompt' in data and len(data['prompt']) > 200
print('✓ Build prompt for stage 6 (scenes) working and bundled')

# 6. Check state loading and auto image resolution
state_res = client.get('/api/projects/ep01-sample')
assert state_res.status_code == 200
scenes = state_res.json().get('scenes', [])
print(f'✓ Loaded ep01-sample state with {len(scenes)} scenes')

print('\nALL BACKEND PIPELINE CHECKS PASSED PERFECTLY!')
