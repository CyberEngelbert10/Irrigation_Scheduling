export interface IrrigationSchedule {
  id: number;
  field: number;
  field_name: string;
  user: number;
  user_email: string;
  predicted_water_amount: string; // Decimal as string
  confidence_score: string; // Decimal as string
  irrigation_reason: string;
  recommended_date: string; // ISO date string
  recommended_time: string; // Time string (HH:MM:SS)
  priority_level: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'confirmed' | 'completed' | 'skipped' | 'cancelled';
  model_input_data?: any; // JSON data
  model_prediction_details?: any; // JSON data
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
  scheduled_at?: string; // ISO datetime string
  is_overdue: boolean;
  days_until_scheduled: number;
}

export interface IrrigationHistory {
  id: number;
  field: number;
  field_name: string;
  user: number;
  user_email: string;
  water_amount_used: string; // Decimal as string
  irrigation_method: 'drip' | 'sprinkler' | 'flood' | 'manual' | 'other';
  irrigation_date: string; // ISO date string
  irrigation_time: string; // Time string (HH:MM:SS)
  duration_minutes: number;
  weather_conditions?: any; // JSON data
  soil_moisture_before?: number;
  soil_moisture_after?: number;
  notes?: string;
  effectiveness_rating?: number; // 1-5
  related_schedule?: number;
  schedule_details?: {
    id: number;
    predicted_amount: string;
    confidence_score: string;
    status: string;
  };
  created_at: string; // ISO datetime string
  updated_at: string; // ISO datetime string
}

export interface WaterUsageStats {
  period_days: number;
  total_water_usage: number;
  average_daily_usage: number;
  usage_by_field: Array<{
    field__name: string;
    total_usage: number;
    irrigation_count: number;
  }>;
  usage_by_method: Array<{
    irrigation_method: string;
    total_usage: number;
    count: number;
  }>;
  monthly_trends: Array<{
    month: string;
    total_usage: number;
    irrigation_count: number;
  }>;
  efficiency_metrics: {
    average_rating: number | null;
    rated_irrigation_count: number;
    total_irrigation_count: number;
  };
  water_efficiency: {
    avg_liters_per_minute: number;
  };
  usage_trend: {
    recent_week_liters: number;
    previous_week_liters: number;
    percentage_change: number | null;
  };
}

export interface FieldAnalytics {
  field_id: number;
  field_name: string;
  period_days: number;
  total_water_usage: number;
  irrigation_count: number;
  avg_usage_per_irrigation: number;
  soil_moisture_trends: Array<{
    irrigation_date: string;
    avg_before: number;
    avg_after: number;
    count: number;
  }>;
  effectiveness_trends: Array<{
    irrigation_date: string;
    avg_rating: number;
    count: number;
  }>;
  weekly_usage: Array<{
    week: string;
    total_usage: number;
    irrigation_count: number;
  }>;
}

export interface EfficiencyReport {
  period_days: number;
  efficiency_analysis: Array<{
    irrigation_method: string;
    effectiveness_rating: number | null;
    count: number;
    avg_rating: number | null;
    total_usage: number;
    avg_duration: number | null;
  }>;
  best_performing_methods: Array<{
    irrigation_method: string;
    effectiveness_rating: number | null;
    count: number;
    avg_rating: number | null;
    total_usage: number;
    avg_duration: number | null;
  }>;
  potential_water_waste: IrrigationHistory[];
  recommendations: Array<{
    type: string;
    title: string;
    description: string;
    priority: 'low' | 'medium' | 'high';
  }>;
  summary: {
    total_irrigation_events: number;
    avg_effectiveness_rating: number | null;
    most_used_method: string | null;
  };
}

export interface FieldPrediction {
  field_id: number;
  field_name: string;
  predicted_water_amount: number;  // L/m² (liters per square meter)
  predicted_water_unit?: string;   // "L/m²"
  total_water_liters?: number;     // Total liters for entire field
  total_water_m3?: number;         // Total cubic meters for entire field
  confidence_score: number;
  input_data: any;
  weather_data: {
    temperature: number;
    humidity: number;
    rainfall: number;
    windspeed: number;
  };
  priority: 'low' | 'medium' | 'high' | 'critical';
  reason: string;
  // User-friendly descriptions
  priority_description?: string;
  water_amount_explanation?: string;
  weather_summary?: string;
  // Field context
  field_info?: {
    crop_type: string;
    crop_days: number;
    soil_moisture: number;
    soil_type: string;
    region: string;
    season: string;
    area_hectares?: number;
    area_m2?: number;
  };
}

export interface ScheduleCreateData {
  field_id: number;
}

export interface ScheduleUpdateData {
  status: 'pending' | 'confirmed' | 'completed' | 'skipped' | 'cancelled';
}

export interface HistoryCreateData {
  field: number;
  water_amount_used: number;
  irrigation_method: 'drip' | 'sprinkler' | 'flood' | 'manual' | 'other';
  irrigation_date: string;
  irrigation_time: string;
  duration_minutes: number;
  weather_conditions?: any;
  soil_moisture_before?: number;
  soil_moisture_after?: number;
  notes?: string;
  effectiveness_rating?: number;
  related_schedule?: number;
}

export interface UserPreferences {
  id: number;
  user: number;
  user_email: string;

  // Notification preferences
  email_notifications: boolean;
  push_notifications: boolean;
  irrigation_reminders: boolean;
  weather_alerts: boolean;
  weekly_reports: boolean;

  // Unit preferences
  temperature_unit: 'celsius' | 'fahrenheit';
  volume_unit: 'liters' | 'gallons';

  // Irrigation defaults
  default_irrigation_method: 'drip' | 'sprinkler' | 'flood' | 'manual' | 'other';
  default_irrigation_duration: number; // minutes
  default_water_amount: number; // in preferred volume unit

  // Display preferences
  dashboard_refresh_interval: number; // minutes
  items_per_page: number;

  // System preferences
  timezone: string;
  language: string;

  created_at: string;
  updated_at: string;
}