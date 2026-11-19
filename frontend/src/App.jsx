import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import PipelineProgressBar from './components/PipelineProgressBar';
import CommandCenter from './components/CommandCenter';
import ScriptView from './components/ScriptView';
import CharacterView from './components/CharacterView';
import SceneView from './components/SceneView';
import AudioView from './components/AudioView';
import EditView from './components/EditView';
import IdeaBibleView from './components/IdeaBibleView';
import PublishView from './components/PublishView';
import SkillViewerModal from './components/SkillViewerModal';
import NewEpisodeModal from './components/NewEpisodeModal';
import UniverseModal from './components/UniverseModal';
import { 
  fetchProjects, 
  fetchProjectState, 
  updateStageStatus, 
  patchProjectState 
} from './api';

export default function App() {
  const [projects, setProjects] = useState([]);
  const [currentEpisodeId, setCurrentEpisodeId] = useState('');
  const [projectState, setProjectState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const loadSeq = useRef(0);

  // Nav state
  const [currentTab, setCurrentTab] = useState('dashboard'); // 'dashboard' or 'stages'
  const [activeStageNumber, setActiveStageNumber] = useState(6); // Default stage to view

  // Modals
  const [isSkillsModalOpen, setIsSkillsModalOpen] = useState(false);
  const [isNewModalOpen, setIsNewModalOpen] = useState(false);
  const [isUniverseModalOpen, setIsUniverseModalOpen] = useState(false);

  // Load project list on mount
  useEffect(() => {
    loadProjects();
  }, []);

  // Load active project state whenever currentEpisodeId changes
  useEffect(() => {
    if (currentEpisodeId) {
      loadEpisodeState(currentEpisodeId);
    } else {
      setProjectState(null);
      setLoading(false);
    }
  }, [currentEpisodeId]);

  const loadProjects = async () => {
    try {
      const data = await fetchProjects();
      const list = data.projects || [];
      setProjects(list);
      setCurrentEpisodeId(prev =>
        prev && list.some(p => p.episode_id === prev) ? prev : (list[0]?.episode_id || ''));
    } catch (err) {
      console.error('Failed to load projects', err);
    }
  };

  const loadEpisodeState = async (episodeId, { silent = false, followStage = false } = {}) => {
    const seq = ++loadSeq.current;
    if (!silent) setLoading(true);
    try {
      const state = await fetchProjectState(episodeId);
      if (seq !== loadSeq.current) return;
      setProjectState(state);
      setLoadError('');
      if (!silent || followStage) setActiveStageNumber(state.current_stage || 1);
    } catch (err) {
      if (seq !== loadSeq.current) return;
      console.error('Failed to load episode state', err);
      if (!silent) {
        setProjectState(null);
        setLoadError('خطا در بارگذاری اپیزود: ' + err.message);
      }
    } finally {
      if (!silent && seq === loadSeq.current) setLoading(false);
    }
  };

  const handleApproveStage = async (stageNumber) => {
    if (!currentEpisodeId) return;
    try {
      await updateStageStatus(currentEpisodeId, stageNumber, 'approved');
      await loadEpisodeState(currentEpisodeId, { silent: true, followStage: true });
      await loadProjects();
    } catch (err) {
      alert('خطا در تایید مرحله: ' + err.message);
    }
  };

  const handleNavigateToStage = (stageNum) => {
    setActiveStageNumber(stageNum);
    setCurrentTab('stages');
  };

  const persistUpdates = async (updates, { withEtag = false } = {}) => {
    if (!projectState || projectState.episode_id !== currentEpisodeId) return false;
    try {
      const res = await patchProjectState(currentEpisodeId, updates, withEtag ? projectState._etag : null);
      setProjectState(prev => (prev ? { ...prev, ...updates, _etag: res._etag || prev._etag } : prev));
      return true;
    } catch (err) {
      alert(err.code === 409
        ? 'محتوای این اپیزود روی دیسک تغییر کرده است (احتمالاً توسط ایجنت). دادهها دوباره بارگذاری میشوند.'
        : 'خطا در ذخیره: ' + err.message);
      await loadEpisodeState(currentEpisodeId, { silent: true });
      return false;
    }
  };
  const sceneKey = (s) => s.scene_id || s.id;

  const handleCharacterUpdated = async (charId, newUrl) => {
    if (!projectState) return;
    await persistUpdates({ characters: projectState.characters.map(c =>
      c.id === charId ? { ...c, turnaround_sheet: newUrl, status: 'approved' } : c) });
  };
  const handleUpdateCharacterStatus = async (charId, newStatus) => {
    if (!projectState) return;
    await persistUpdates({ characters: projectState.characters.map(c =>
      c.id === charId ? { ...c, status: newStatus } : c) });
  };
  const handleSceneAssetUpdated = async (sceneId, field, value) => {
    if (!projectState || (field !== 'image_path' && field !== 'video_path')) return;
    const scenes = projectState.scenes.map(s => {
      if (sceneKey(s) !== sceneId) return s;
      return field === 'image_path'
        ? { ...s, image_path: value, visual_asset: value, image_version: Date.now() }
        : { ...s, video_path: value };
    });
    await persistUpdates({ scenes }, { withEtag: true });
  };
  const handleUpdateSceneStatus = async (sceneId, newStatus) => {
    if (!projectState) return;
    await persistUpdates({ scenes: projectState.scenes.map(s =>
      sceneKey(s) === sceneId ? { ...s, status: newStatus } : s) }, { withEtag: true });
  };
  const handleAudioUpdated = async (segmentId, newUrl) => {
    if (!projectState) return;
    const tracks = (projectState.audio?.tracks || []).map(t =>
      (t.segment_id || t.id) === segmentId ? { ...t, audio_file: newUrl, status: 'recorded' } : t);
    await persistUpdates({ audio: { ...projectState.audio, tracks } });
  };

  const getStageStatus = (num) => {
    return projectState?.stages?.find(s => s.stage_number === num)?.status || 'pending';
  };

  return (
    <div className="min-h-screen bg-[#090D16] text-slate-100 flex flex-col font-sans">
      
      {/* Top Navbar */}
      <Header
        projects={projects}
        currentEpisodeId={currentEpisodeId}
        onSelectEpisode={(id) => setCurrentEpisodeId(id)}
        onOpenNewModal={() => setIsNewModalOpen(true)}
        onOpenSkillsModal={() => setIsSkillsModalOpen(true)}
        onOpenUniverseModal={() => setIsUniverseModalOpen(true)}
        currentTab={currentTab}
        onSelectTab={(tab) => setCurrentTab(tab)}
      />

      {/* 9-Stage Pipeline Stepper */}
      {projectState && (
        <PipelineProgressBar
          stages={projectState.stages}
          currentStage={projectState.current_stage || 1}
          activeViewStage={activeStageNumber}
          onSelectStage={(stageNum) => handleNavigateToStage(stageNum)}
        />
      )}

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {loading ? (
          <div className="flex items-center justify-center py-24 text-slate-400 text-sm">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400 animate-ping" />
              در حال بارگذاری پروژه و اطلاعات استودیو...
            </div>
          </div>
        ) : !projectState ? (
          <div className="py-16 text-center space-y-3">
            <p className="text-sm text-rose-300">{loadError || 'اپیزودی انتخاب نشده است.'}</p>
            {currentEpisodeId && (
              <button onClick={() => loadEpisodeState(currentEpisodeId)}
                className="px-4 py-2 rounded-xl bg-amber-500 text-slate-950 text-xs font-bold">تلاش مجدد</button>
            )}
          </div>
        ) : (
          <>
            {/* Dashboard View ("استودیو امروز") */}
            {currentTab === 'dashboard' && (
              <CommandCenter
                projectState={projectState}
                onNavigateToStage={(stageNum) => handleNavigateToStage(stageNum)}
                onApproveStage={(stageNum) => handleApproveStage(stageNum)}
                onRefresh={() => loadEpisodeState(currentEpisodeId, { silent: true })}
              />
            )}

            {/* Stages View (9 Distinct Stage Panels) */}
            {currentTab === 'stages' && (
              <div>
                {/* Stage 1 & 2: Idea & Bible */}
                {(activeStageNumber === 1 || activeStageNumber === 2) && (
                  <IdeaBibleView
                    stageNumber={activeStageNumber}
                    ideaData={projectState?.idea}
                    bibleData={projectState?.bible}
                    episodeId={currentEpisodeId}
                    stageStatus={getStageStatus(activeStageNumber)}
                    onApproveStage={() => handleApproveStage(activeStageNumber)}
                    onRefresh={() => loadEpisodeState(currentEpisodeId, { silent: true })}
                  />
                )}

                {/* Stage 3: Script View */}
                {activeStageNumber === 3 && (
                  <ScriptView
                    scriptData={projectState?.script}
                    episodeId={currentEpisodeId}
                    stageStatus={getStageStatus(3)}
                    onApprove={() => handleApproveStage(3)}
                    onSaveScript={(updated) => persistUpdates({ script: updated })}
                    onRefresh={() => loadEpisodeState(currentEpisodeId, { silent: true })}
                  />
                )}

                {/* Stage 4: Character View */}
                {activeStageNumber === 4 && (
                  <CharacterView
                    characters={projectState?.characters}
                    episodeId={currentEpisodeId}
                    stageStatus={getStageStatus(4)}
                    onApproveStage={() => handleApproveStage(4)}
                    onUpdateCharacterStatus={handleUpdateCharacterStatus}
                    onCharacterUpdated={handleCharacterUpdated}
                    onRefresh={() => loadEpisodeState(currentEpisodeId, { silent: true })}
                  />
                )}

                {/* Stage 5: Audio & Mix View */}
                {activeStageNumber === 5 && (
                  <AudioView
                    audioData={projectState?.audio}
                    episodeId={currentEpisodeId}
                    stageStatus={getStageStatus(5)}
                    onApproveStage={() => handleApproveStage(5)}
                    onAudioUpdated={handleAudioUpdated}
                  />
                )}

                {/* Stage 6: Scenes View */}
                {activeStageNumber === 6 && (
                  <SceneView
                    scenes={projectState?.scenes}
                    episodeId={currentEpisodeId}
                    stageStatus={getStageStatus(6)}
                    onApproveStage={() => handleApproveStage(6)}
                    onUpdateSceneStatus={handleUpdateSceneStatus}
                    onSceneAssetUpdated={handleSceneAssetUpdated}
                    onRefresh={() => loadEpisodeState(currentEpisodeId, { silent: true })}
                  />
                )}

                {/* Stage 7: Edit View (FFmpeg & Subtitles) */}
                {activeStageNumber === 7 && (
                  <EditView
                    editData={projectState?.edit}
                    episodeId={currentEpisodeId}
                    stageStatus={getStageStatus(7)}
                    onApproveStage={() => handleApproveStage(7)}
                  />
                )}

                {/* Stage 8 & 9: Publish & Analytics */}
                {(activeStageNumber === 8 || activeStageNumber === 9) && (
                  <PublishView
                    stageNumber={activeStageNumber}
                    publishData={projectState?.publish}
                    analyticsData={projectState?.analytics}
                    stageStatus={getStageStatus(activeStageNumber)}
                    onApproveStage={() => handleApproveStage(activeStageNumber)}
                  />
                )}
              </div>
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-4 text-center text-xs text-slate-500">
        <p>استودیو کمدی و آموزش پوکر ایرانی • طراحی شده با پایپ‌لاین تولید مستقیم عامل هوشمند Antigravity</p>
      </footer>

      {/* Modals */}
      <SkillViewerModal
        isOpen={isSkillsModalOpen}
        onClose={() => setIsSkillsModalOpen(false)}
      />

      <NewEpisodeModal
        isOpen={isNewModalOpen}
        onClose={() => setIsNewModalOpen(false)}
        onCreated={(newId) => {
          loadProjects();
          setCurrentEpisodeId(newId);
          setActiveStageNumber(1);
          setCurrentTab('stages');
        }}
      />

      <UniverseModal
        isOpen={isUniverseModalOpen}
        onClose={() => setIsUniverseModalOpen(false)}
        onUniverseUpdated={() => {
          loadProjects();
          if (currentEpisodeId) loadEpisodeState(currentEpisodeId, { silent: true });
        }}
      />

    </div>
  );
}
