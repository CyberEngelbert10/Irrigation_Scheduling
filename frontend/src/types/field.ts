export interface Field {
  id: number;
  user_email: string;
  user_name: string;
  name: string;
  location?: string;
  region: string;
  region_display: string;
  latitude?: number;
  longitude?: number;
  area: number;
  crop_type: string;
  crop_type_display: string;
  planting_date: string; // ISO date string
  crop_days: number;
  crop_age_weeks: number;
  soil_type: string;
  soil_type_display: string;
  current_soil_moisture: number;
  irrigation_method: string;
  irrigation_method_display: string;
  current_season: string;
  season_display: string;
  notes?: string;
  is_active: boolean;
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

export interface FieldCreateData {
  name: string;
  location?: string;
  region: string;
  latitude?: number;
  longitude?: number;
  area: number;
  crop_type: string;
  planting_date: string;
  soil_type: string;
  current_soil_moisture: number;
  irrigation_method: string;
  current_season: string;
  notes?: string;
  is_active: boolean;
}

export interface FieldUpdateData extends Partial<FieldCreateData> {}

export interface FieldListItem {
  id: number;
  name: string;
  crop_type: string;
  crop_type_display: string;
  region_display: string;
  area: number;
  is_active: boolean;
  planting_date: string;
  crop_days: number;
}

export interface FieldStatistics {
  total_fields: number;
  active_fields: number;
  inactive_fields: number;
  total_area_hectares: number;
  crop_distribution: Record<string, number>;
  region_distribution: Record<string, number>;
}

export const REGIONS = [
  { value: 'lusaka', label: 'Lusaka' },
  { value: 'central', label: 'Central Province' },
  { value: 'southern', label: 'Southern Province' },
  { value: 'eastern', label: 'Eastern Province' },
  { value: 'copperbelt', label: 'Copperbelt' },
  { value: 'northern', label: 'Northern Province' },
  { value: 'western', label: 'Western Province' },
  { value: 'luapula', label: 'Luapula Province' },
  { value: 'muchinga', label: 'Muchinga Province' },
  { value: 'northwestern', label: 'North-Western Province' },
] as const;

export const CROPS = [
  { value: 'Maize', label: 'Maize' },
  { value: 'Wheat', label: 'Wheat' },
  { value: 'Rice', label: 'Rice' },
  { value: 'Tomatoes', label: 'Tomatoes' },
  { value: 'Potatoes', label: 'Potatoes' },
  { value: 'Cotton', label: 'Cotton' },
] as const;

export const SOIL_TYPES = [
  { value: 'Clay', label: 'Clay' },
  { value: 'Loam', label: 'Loam' },
  { value: 'Sandy', label: 'Sandy' },
  { value: 'Silty', label: 'Silty' },
] as const;

export const IRRIGATION_METHODS = [
  { value: 'drip', label: 'Drip Irrigation' },
  { value: 'sprinkler', label: 'Sprinkler' },
  { value: 'flood', label: 'Flood Irrigation' },
  { value: 'rainfed', label: 'Rainfed (No Irrigation)' },
] as const;

export const SEASONS = [
  { value: 'Dry', label: 'Dry Season (May-October)' },
  { value: 'Wet', label: 'Wet Season (November-April)' },
] as const;
