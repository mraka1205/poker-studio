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

export async function uploadAsset(episodeId, targetType, file) {
  const formData = new FormData();
  formData.append('target_type', targetType);
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/projects/${episodeId}/upload/${targetType}`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    // Fallback to legacy endpoint if needed
    const res2 = await fetch(`${API_BASE}/projects/${episodeId}/upload`, {
      method: 'POST',
      body: formData
    });
    if (!res2.ok) throw new Error('Failed to upload file');
    return res2.json();
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
  try {
    return await buildAiStudioPrompt(episodeId, stage);
  } catch (err) {
    return {
      episode_id: episodeId,
      skill_file: '02-persian-script-writer.md',
      stage_desc: 'نگارش سناریو کمدی با هوش مصنوعی',
      prompt: 'پرامپت در حال آماده‌سازی است...'
    };
  }
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
// AI STUDIO BRIDGE & OPENROUTER API
// ==========================================

export async function buildAiStudioPrompt(episodeId, stage) {
  const res = await fetch(`${API_BASE}/projects/${episodeId}/build-prompt/${stage}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to build AI Studio prompt');
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

export async function runOpenRouterTask(episodeId, task, model = null, taskData = null) {
  const res = await fetch(`${API_BASE}/projects/${episodeId}/run-openrouter/${task}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model, task_data: taskData })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to execute OpenRouter task');
  }
  return res.json();
}

export async function fetchSettings() {
  const res = await fetch(`${API_BASE}/settings`);
  if (!res.ok) throw new Error('Failed to fetch settings');
  return res.json();
}

export async function saveSettings(openrouterApiKey, openrouterModel, geminiApiKey = null, geminiModel = null) {
  const payload = {};
  if (openrouterApiKey !== undefined && openrouterApiKey !== null) payload.openrouter_api_key = openrouterApiKey;
  if (openrouterModel !== undefined && openrouterModel !== null) payload.openrouter_model = openrouterModel;
  if (geminiApiKey !== undefined && geminiApiKey !== null) payload.gemini_api_key = geminiApiKey;
  if (geminiModel !== undefined && geminiModel !== null) payload.gemini_model = geminiModel;

  const res = await fetch(`${API_BASE}/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Failed to save settings');
  return res.json();
}

export async function fetchGeminiModels(key = null) {
  const url = key ? `${API_BASE}/gemini/models?key=${encodeURIComponent(key)}` : `${API_BASE}/gemini/models`;
  const res = await fetch(url);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to fetch Gemini models');
  }
  return res.json();
}

export async function fetchOpenRouterModels(key = null) {
  const url = key ? `${API_BASE}/openrouter/models?key=${encodeURIComponent(key)}` : `${API_BASE}/openrouter/models`;
  const res = await fetch(url);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to fetch OpenRouter models');
  }
  return res.json();
}

export async function runGeminiStage(episodeId, stage, model = null, temperature = 0.4) {
  const res = await fetch(`${API_BASE}/projects/${episodeId}/run-gemini/${stage}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model, temperature })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to run Gemini stage');
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

export async function rewriteScenePrompt(episodeId, sceneId, target, feedback, model = null) {
  const res = await fetch(`${API_BASE}/projects/${episodeId}/scenes/${sceneId}/rewrite-prompt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ target, feedback, model })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to rewrite prompt');
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

export async function generateCharacterPrompts(characterId, { concept_fa, name_fa, archetype, flow_tag, model } = {}) {
  const res = await fetch(`${API_BASE}/universe/characters/${characterId}/generate-prompts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ concept_fa, name_fa, archetype, flow_tag, model })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to generate character prompts');
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
