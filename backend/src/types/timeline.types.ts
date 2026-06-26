export interface TimelineItem {
  id: string;
  label: string;
  start: string;
  end: string;
  count: number;
  /** Normalised article density: 0.0 (least active) → 1.0 (most active) */
  intensity: number;
}
