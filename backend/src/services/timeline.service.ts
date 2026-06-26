import { clustersRepository } from '../repositories/clusters.repository';
import { TimelineItem } from '../types/timeline.types';
export const timelineService = {
  async getTimeline(): Promise<TimelineItem[]> {
    const clusters = await clustersRepository.findAllWithTimeRange();
    const withTimes = clusters.filter(
      (c): c is typeof c & { startTime: string; endTime: string } =>
        c.startTime !== null && c.endTime !== null,
    );
    if (withTimes.length === 0) {
      return [];
    }
    const maxCount = Math.max(...withTimes.map((c) => c.articleCount));
    const items: TimelineItem[] = withTimes.map((c) => ({
      id: c.id,
      label: c.label,
      start: c.startTime,
      end: c.endTime,
      count: c.articleCount,
      intensity: maxCount > 0 ? c.articleCount / maxCount : 0,
    }));
    items.sort(
      (a, b) => new Date(a.start).getTime() - new Date(b.start).getTime(),
    );
    return items;
  },
};