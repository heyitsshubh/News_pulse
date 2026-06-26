import { configureStore } from '@reduxjs/toolkit';
import { newsApi } from './api/newsApi';
import timelineReducer from './slices/timelineSlice';
import ingestReducer from './slices/ingestSlice';
import filtersReducer from './slices/filtersSlice';
export const store = configureStore({
  reducer: {
    [newsApi.reducerPath]: newsApi.reducer,
    timeline: timelineReducer,
    ingest: ingestReducer,
    filters: filtersReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(newsApi.middleware),
});
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;