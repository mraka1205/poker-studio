const API_BASE = '/api';

export async function fetchProjects() {
  const res = await fetch(`${API_BASE}/projects`);
  if (!res.ok) throw new Error('Failed to fetch projects');
  return res.json();
}

export async function fetchProjectState(episodeId) {
  const res = await fetch(`${API_BASE}/projects/${episodeId}`);
  if (!res.ok) throw new Error('Failed to fetch project state');
  return res.json();
}

export async function saveProjectState(episodeId, state) {
  const res = await fetch(`${API_BASE}/projects/${episodeId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(state)
  });
  if (!res.ok) throw new Error('Failed to save project state');
  return res.json();
}

export async function patchProjectState(episodeId, updates, baseEtag = null) {
  const res = await fetch(`${API_BASE}/projects/${episodeId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ updates, base_etag: baseEtag })
  });
  if (res.status === 409) {
    const e = new Error('STATE_CONFLICT');
    e.code = 409;
    throw e;
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to save changes');
  }
  return res.json();
}

export async function updateStageStatus(episodeId, stageNumber, status, notes = '') {
  const res = await fetch(`${API_BASE}/projects/${episodeId}/stage_status`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ stage_number: stageNumber, status, notes })
  });
  if (!res.ok) throw new Error('Failed to update stage status');
  return res.json();
}

export async function setEpisodeCurrentStage(episodeId, currentStage) {
  const res = await fetch(`${API_BASE}/projects/${episodeId}/set_stage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ current_stage: currentStage })
  });
  if (!res.ok) throw new Error('Failed to set current stage');
  return res.json();
}

export async function uploadAsset(episodeId, targetType, file, extraFields = {}) {
  const build = () => {
    const fd = new FormData();
    fd.append('target_type', targetType);
    fd.append('file', file);
    Object.entries(extraFields).forEach(([k, v]) => fd.append(k, v));
    return fd;
  };
  let res = await fetch(`${API_BASE}/projects/${episodeId}/upload/${targetType}`, { method: 'POST', body: build() });
  if (res.status === 404 || res.status === 405) {
    res = await fetch(`${API_BASE}/projects/${episodeId}/upload`, { method: 'POST', body: build() });
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to upload file');
  }
  return res.json();
}

export async function generateSubtitles(episodeId, includeTts = false) {
  const res = await fetch(`${API_BASE}/projects/${episodeId}/generate_subtitles`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ include_tts: includeTts })
  });
  if (!res.ok) throw new Error('Failed to generate subtitles');
  return res.json();
}

export async function fetchFfmpegCommand(episodeId) {
  const res = await fetch(`${API_BASE}/projects/${episodeId}/render_ffmpeg_preview`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to fetch FFmpeg command');
  return res.json();
}

export async function saveEpisodeIdea(episodeId, { raw_hand_or_concept, theme, core_lesson }) {
  const res = await fetch(`${API_BASE}/projects/${episodeId}/save-idea`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ raw_hand_or_concept, theme, core_lesson })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to save episode idea');
  }
  return res.json();
}

export async function createNewEpisode(episodeData) {
  const res = await fetch(`${API_BASE}/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(episodeData)
  });
  if (!res.ok) throw new Error('Failed to create episode');
  return res.json();
}

export async function fetchAgentPrompt(episodeId, stage = 'script') {
  return buildAiStudioPrompt(episodeId, stage);
}

export async function fetchSkills() {
  const res = await fetch(`${API_BASE}/skills`);
  if (!res.ok) throw new Error('Failed to fetch skills');
  return res.json();
}

export async function fetchSkillDetail(filename) {
  const res = await fetch(`${API_BASE}/skills/${filename}`);
  if (!res.ok) throw new Error('Failed to fetch skill content');
  return res.json();
}

// ==========================================
// ANTIGRAVITY AGENT PROMPT BUILDER & STATE
// ==========================================

export async function buildAiStudioPrompt(episodeId, stage) {
  const res = await fetch(`${API_BASE}/projects/${episodeId}/build-prompt/${stage}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to build stage prompt');
  }
  return res.json();
}

export async function importAiStudioJson(episodeId, stage, jsonContent) {
  const res = await fetch(`${API_BASE}/projects/${episodeId}/import-json/${stage}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ json_content: jsonContent })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to import JSON');
  }
  return res.json();
}

export async function uploadSceneVideo(episodeId, sceneId, file) {
  const formData = new FormData();
  formData.append('scene_id', sceneId);
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/projects/${episodeId}/upload/scene_video`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to upload scene video');
  }
  return res.json();
}

export async function updateSceneDetails(episodeId, sceneId, updates) {
  const res = await fetch(`${API_BASE}/projects/${episodeId}/scenes/${sceneId}/update`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to update scene');
  }
  return res.json();
}

// ==========================================
// CHANNEL UNIVERSE (Fixed Room & Global Cast)
// ==========================================

export async function fetchUniverse() {
  const res = await fetch(`${API_BASE}/universe`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to fetch universe data');
  }
  return res.json();
}

export async function saveUniverse(universeData) {
  const res = await fetch(`${API_BASE}/universe`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(universeData)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to save universe data');
  }
  return res.json();
}

export async function uploadUniverseAsset(assetType, file, characterId = null, angleId = null, sheetType = null) {
  const formData = new FormData();
  formData.append('file', file);
  if (characterId) {
    formData.append('character_id', characterId);
  }
  if (angleId) {
    formData.append('angle_id', angleId);
  }
  if (sheetType) {
    formData.append('sheet_type', sheetType);
  }
  const res = await fetch(`${API_BASE}/universe/upload/${assetType}`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to upload universe asset');
  }
  return res.json();
}

export async function syncUniverseCharacters(episodeId, characterIds) {
  const res = await fetch(`${API_BASE}/projects/${episodeId}/sync-universe-characters`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ character_ids: characterIds })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to sync universe characters');
  }
  return res.json();
}

export async function updateCharacterSeat(episodeId, charId, seat) {
  const res = await fetch(`${API_BASE}/projects/${episodeId}/characters/${charId}/seat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ seat })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to update character seat');
  }
  return res.json();
}

export async function triggerStoryboardGeneration(episodeId) {
  const res = await fetch(`${API_BASE}/episodes/${episodeId}/generate-storyboard`, {
    method: 'POST'
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to start storyboard generation');
  }
  return res.json();
}

export async function triggerImagesGeneration(episodeId) {
  const res = await fetch(`${API_BASE}/episodes/${episodeId}/generate-images`, {
    method: 'POST'
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to start images generation');
  }
  return res.json();
}

export async function triggerSceneRegeneration(episodeId, sceneId) {
  const res = await fetch(`${API_BASE}/episodes/${episodeId}/scenes/${sceneId}/regenerate-image`, {
    method: 'POST'
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to start scene regeneration');
  }
  return res.json();
}

export async function fetchTaskStatus(episodeId) {
  const res = await fetch(`${API_BASE}/episodes/${episodeId}/task-status`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to fetch task status');
  }
  return res.json();
}

export async function cancelTask(episodeId) {
  const res = await fetch(`${API_BASE}/episodes/${episodeId}/cancel-task`, { method: 'POST' });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to cancel task');
  }
  return res.json();
}
