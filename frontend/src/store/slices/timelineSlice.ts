import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface TimelineState {
  selectedClusterId: string | null;
}

const initialState: TimelineState = {
  selectedClusterId: null,
};

const timelineSlice = createSlice({
  name: 'timeline',
  initialState,
  reducers: {
    setSelectedCluster(state, action: PayloadAction<string>) {
      state.selectedClusterId = action.payload;
    },
    clearSelectedCluster(state) {
      state.selectedClusterId = null;
    },
  },
});

export const { setSelectedCluster, clearSelectedCluster } = timelineSlice.actions;
export default timelineSlice.reducer;
