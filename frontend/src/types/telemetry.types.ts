/**
 * Telemetry Types — matches exact backend response shapes.
 * DO NOT add fields that the backend does not supply.
 */

/** Response from GET /api/v1/telemetry/sentinel-surface-map */
export interface SentinelSurfaceMapResponse {
  status: 'connected' | 'feed_pending' | string;
  feed_available: boolean;
  satellite?: string;
  message: string;
  viewport?: {
    latitude: number;
    longitude: number;
    radius_km: number;
  };
  vegetation_indices?: {
    mean_ndvi: number;
    mean_ndwi: number;
    canopy_vigor: string;
  } | null;
  tile_layer_url?: string;
}

/** One entry from GET /api/v1/early-warning/alerts active_alerts array */
export interface LiveAlertEntry {
  id: string;
  severity: string;          // "HIGH" | "MODERATE" | "LOW"
  type: string | null;
  confidence: number;
  proactive_actions: string[];
  spoken_advisory: string;
  detected_at: string;       // ISO timestamp
}

/** Response from GET /api/v1/early-warning/alerts */
export interface EarlyWarningAlertsResponse {
  status: 'connected' | 'feed_pending' | string;
  alerts_count: number;
  message: string;
  active_alerts: LiveAlertEntry[];
}

/** Response from GET /api/v1/telemetry/agro-climatic-zones */
export interface AgroClimaticZonesResponse {
  type: string;
  features: any[]; // Using any[] for geojson features to keep it minimal and flexible
}

export interface WeatherCurrentConditions {
  temperature_c: number | null;
  humidity_pct: number | null;
  precipitation_mm: number;
  wind_speed_kmh: number;
  weather_code: number | null;
  next_12h_rain_chance_pct: number;
  spray_advisory: 'SAFE_TO_SPRAY' | 'DO_NOT_SPRAY';
}

export interface WeatherDailyForecast {
  date: string;
  temp_max_c: number | null;
  temp_min_c: number | null;
  rain_chance_max_pct: number | null;
  total_precipitation_mm: number | null;
  weather_code: number | null;
}

export interface WeatherForecastData {
  latitude: number;
  longitude: number;
  timezone: string;
  current: WeatherCurrentConditions;
  daily_forecast: WeatherDailyForecast[];
}

export interface WeatherForecastResponse {
  status: 'success';
  data: WeatherForecastData;
}