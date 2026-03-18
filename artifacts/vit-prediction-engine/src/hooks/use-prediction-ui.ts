import { create } from 'zustand';

interface PredictionUIState {
  activePredictionId: number | null;
  setActivePredictionId: (id: number | null) => void;
  isFormOpen: boolean;
  setFormOpen: (isOpen: boolean) => void;
}

// Simple store to manage the active view between the prediction history and the new analysis form
export const usePredictionUI = create<PredictionUIState>((set) => ({
  activePredictionId: null,
  setActivePredictionId: (id) => set({ activePredictionId: id, isFormOpen: id === null }),
  isFormOpen: true,
  setFormOpen: (isOpen) => set({ isFormOpen: isOpen, activePredictionId: isOpen ? null : undefined }),
}));
