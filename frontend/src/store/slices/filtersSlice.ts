import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { SOURCES } from '../../lib/constants';
interface FiltersState {
  activeSources: string[];
}
const initialState: FiltersState = {
  activeSources: SOURCES.map((s) => s.key),
};
const filtersSlice = createSlice({
  name: 'filters',
  initialState,
  reducers: {
    toggleSource(state, action: PayloadAction<string>) {
      const source = action.payload;
      if (state.activeSources.includes(source)) {
        state.activeSources = state.activeSources.filter((s) => s !== source);
      } else {
        state.activeSources = [...state.activeSources, source];
      }
    },
    setAllSources(state) {
      state.activeSources = SOURCES.map((s) => s.key);
    },
    clearSources(state) {
      state.activeSources = [];
    },
  },
});
export const { toggleSource, setAllSources, clearSources } = filtersSlice.actions;
export default filtersSlice.reducer;