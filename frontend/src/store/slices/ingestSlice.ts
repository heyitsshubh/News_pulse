import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface IngestState {
  activeJobId: string | null;
  isPolling: boolean;
  lastRefreshed: string | null;
}

const initialState: IngestState = {
  activeJobId: null,
  isPolling: false,
  lastRefreshed: null,
};

const ingestSlice = createSlice({
  name: 'ingest',
  initialState,
  reducers: {
    setActiveJob(state, action: PayloadAction<string>) {
      state.activeJobId = action.payload;
      state.isPolling = true;
    },
    clearJob(state) {
      state.activeJobId = null;
      state.isPolling = false;
    },
    setPolling(state, action: PayloadAction<boolean>) {
      state.isPolling = action.payload;
    },
    setLastRefreshed(state, action: PayloadAction<string>) {
      state.lastRefreshed = action.payload;
    },
  },
});

export const { setActiveJob, clearJob, setPolling, setLastRefreshed } = ingestSlice.actions;
export default ingestSlice.reducer;
