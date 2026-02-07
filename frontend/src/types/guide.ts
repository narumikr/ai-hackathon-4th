import type { Location } from './travel';

export interface HistoricalEvent {
  year: number;
  event: string;
  significance: string;
  relatedSpots: string[];
}

export interface SpotDetail {
  spotName: string;
  historicalBackground: string;
  highlights: string[];
  recommendedVisitTime: string;
  historicalSignificance: string;
  imageUrl?: string | null;
  imageStatus?: 'not_started' | 'processing' | 'succeeded' | 'failed';
}

export interface Checkpoint {
  spotName: string;
  checkpoints: string[];
  historicalContext: string;
}

export interface MapMarker {
  lat: number;
  lng: number;
  label: string;
}

export interface MapData {
  center: Location;
  zoom: number;
  markers: MapMarker[];
}

export interface TravelGuideResponse {
  id: string;
  planId: string;
  overview: string;
  timeline: HistoricalEvent[];
  spotDetails: SpotDetail[];
  checkpoints: Checkpoint[];
  mapData: MapData;
  createdAt: string;
  updatedAt: string;
}

export interface GenerateTravelGuideRequest {
  planId: string;
}
