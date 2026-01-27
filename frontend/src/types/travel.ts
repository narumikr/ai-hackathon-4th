import type { TravelGuideResponse } from './guide';
import type { ReflectionResponse } from './reflection';

export type TravelPlanStatus = 'planning' | 'completed';
export type GenerationStatus = 'not_started' | 'processing' | 'succeeded' | 'failed';

export interface Location {
  lat: number;
  lng: number;
}

export interface TouristSpot {
  id?: string | null;
  name: string;
  description?: string | null;
  userNotes?: string | null;
}

export interface CreateTravelPlanRequest {
  userId: string;
  title: string;
  destination: string;
  spots?: TouristSpot[];
}

export interface UpdateTravelPlanRequest {
  title?: string | null;
  destination?: string | null;
  spots?: TouristSpot[] | null;
  status?: TravelPlanStatus | null;
}

export interface TravelPlanResponse {
  id: string;
  userId: string;
  title: string;
  destination: string;
  spots: TouristSpot[];
  status: TravelPlanStatus;
  guideGenerationStatus: GenerationStatus;
  reflectionGenerationStatus: GenerationStatus;
  createdAt: string;
  updatedAt: string;
  guide?: TravelGuideResponse | null;
  reflection?: ReflectionResponse | null;
}
