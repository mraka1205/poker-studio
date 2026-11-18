import React, { useState, useEffect } from 'react';
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
import SettingsModal from './components/SettingsModal';
import UniverseModal from './components/UniverseModal';
import { 
  fetchProjects, 
  fetchProjectState, 
  updateStageStatus, 
  saveProjectState 
} from './api';

export default function App() {
  const [projects, setProjects] = useState([]);
  const [currentEpisodeId, setCurrentEpisodeId] = useState('ep01-sample');
  const [projectState, setProjectState] = useState(null);
  const [loading, setLoading] = useState(true);

  // Nav state
  const [currentTab, setCurrentTab] = useState('dashboard'); // 'dashboard' or 'stages'
  const [activeStageNumber, setActiveStageNumber] = useState(3); // Default stage to view

  // Modals
  const [isSkillsModalOpen, setIsSkillsModalOpen] = useState(false);
  const [isNewModalOpen, setIsNewModalOpen] = useState(false);
  const [isSettingsModalOpen, setIsSettingsModalOpen] = useState(false);
  const [isUniverseModalOpen, setIsUniverseModalOpen] = useState(false);

  // Load project list on mount
  useEffect(() => {
    loadProjects();
  }, []);

  // Load active project state whenever currentEpisodeId changes
  useEffect(() => {
    if (currentEpisodeId) {
      loadEpisodeState(currentEpisodeId);
    }
  }, [currentEpisodeId]);

  const loadProjects = async () => {
    try {
      const data = await fetchProjects();
      setProjects(data.projects || []);
      if (data.projects && data.projects.length > 0 && !currentEpisodeId) {
        setCurrentEpisodeId(data.projects[0].episode_id);
      }
    } catch (err) {
      console.error('Failed to load projects', err);
    }
  };

  const loadEpisodeState = async (episodeId) => {
    setLoading(true);
    try {
      const state = await fetchProjectState(episodeId);
      setProjectState(state);
      setActiveStageNumber(state.current_stage || 1);
    } catch (err) {
      console.error('Failed to load episode state', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApproveStage = async (stageNumber) => {
    if (!currentEpisodeId) return;
    try {
      await updateStageStatus(currentEpisodeId, stageNumber, 'approved');
      await loadEpisodeState(currentEpisodeId);
      await loadProjects();
    } catch (err) {
      alert('خطا در تایید مرحله: ' + err.message);
    }
  };

  const handleNavigateToStage = (stageNum) => {
    setActiveStageNumber(stageNum);
    setCurrentTab('stages');
  };

  const handleCharacterUpdated = async (charId, newUrl) => {
    if (!projectState) return;
    const updatedChars = projectState.characters.map(c => 
      c.id === charId ? { ...c, turnaround_sheet: newUrl, status: 'approved' } : c
    );
    const updatedState = { ...projectState, characters: updatedChars };
    setProjectState(updatedState);
    await saveProjectState(currentEpisodeId, updatedState);
  };

  const handleUpdateCharacterStatus = async (charId, newStatus) => {
    if (!projectState) return;
    const updatedChars = projectState.characters.map(c => 
      c.id === charId ? { ...c, status: newStatus } : c
    );
    const updatedState = { ...projectState, characters: updatedChars };
    setProjectState(updatedState);
    await saveProjectState(currentEpisodeId, updatedState);
  };

  const handleSceneAssetUpdated = async (sceneId, newUrl) => {
    if (!projectState) return;
    const updatedScenes = projectState.scenes.map(s => 
      s.id === sceneId ? { ...s, visual_asset: newUrl, status: 'approved' } : s
    );
    const updatedState = { ...projectState, scenes: updatedScenes };
    setProjectState(updatedState);
    await saveProjectState(currentEpisodeId, updatedState);
  };

  const handleUpdateSceneStatus = async (sceneId, newStatus) => {
    if (!projectState) return;
    const updatedScenes = projectState.scenes.map(s => 
      s.id === sceneId ? { ...s, status: newStatus } : s
    );
    const updatedState = { ...projectState, scenes: updatedScenes };
    setProjectState(updatedState);
    await saveProjectState(currentEpisodeId, updatedState);
  };

  const handleAudioUpdated = async (segmentId, newUrl) => {
    if (!projectState) return;
    const updatedTracks = (projectState.audio?.tracks || []).map(t => 
      t.segment_id === segmentId ? { ...t, audio_file: newUrl, status: 'recorded' } : t
    );
    const updatedState = { 
      ...projectState, 
      audio: { ...projectState.audio, tracks: updatedTracks } 
    };
    setProjectState(updatedState);
    await saveProjectState(currentEpisodeId, updatedState);
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
        onOpenSettingsModal={() => setIsSettingsModalOpen(true)}
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
          onApproveCurrentStage={() => handleApproveStage(projectState.current_stage)}
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
        ) : (
          <>
            {/* Dashboard View ("استودیو امروز") */}
            {currentTab === 'dashboard' && (
              <CommandCenter
                projectState={projectState}
                onNavigateToStage={(stageNum) => handleNavigateToStage(stageNum)}
                onApproveStage={(stageNum) => handleApproveStage(stageNum)}
                onRefresh={() => loadEpisodeState(currentEpisodeId)}
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
                    onRefresh={() => loadEpisodeState(currentEpisodeId)}
                  />
                )}

                {/* Stage 3: Script View */}
                {activeStageNumber === 3 && (
                  <ScriptView
                    scriptData={projectState?.script}
                    episodeId={currentEpisodeId}
                    stageStatus={getStageStatus(3)}
                    onApprove={() => handleApproveStage(3)}
                    onSaveScript={(updated) => {
                      saveProjectState(currentEpisodeId, { ...projectState, script: updated });
                      setProjectState(prev => ({ ...prev, script: updated }));
                    }}
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
                    onRefresh={() => loadEpisodeState(currentEpisodeId)}
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
                    onRefresh={() => loadEpisodeState(currentEpisodeId)}
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
        <p>استودیو کمدی و آموزش پوکر ایرانی • طراحی شده با معماری هیبرید Google AI Studio + OpenRouter + نظارت انسان</p>
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

      <SettingsModal
        isOpen={isSettingsModalOpen}
        onClose={() => setIsSettingsModalOpen(false)}
      />

      <UniverseModal
        isOpen={isUniverseModalOpen}
        onClose={() => setIsUniverseModalOpen(false)}
        onUniverseUpdated={() => {
          loadProjects();
          if (currentEpisodeId) loadEpisodeState(currentEpisodeId);
        }}
      />

    </div>
  );
}
