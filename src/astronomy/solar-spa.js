// Local, audited distribution of sunrise-sunset-js 3.3.1 (NREL SPA).
// The adapter keeps the app's UTC Date and WGS84 field contracts stable.
import {
  getSolarPosition,
  getSunTimes,
} from '../../vendor/sunrise-sunset-js/dist/index.js';

export function getSpaPosition(instant, point) {
  const result = getSolarPosition(point.latitude, point.longitude, instant, {
    elevation: point.elevationMeters ?? 0,
    timezone: 8,
  });
  if (!result) return null;
  return { altitudeDeg: result.elevation, azimuthDeg: result.azimuth };
}

export function getSpaEvents(dateIso, point) {
  const date = new Date(`${dateIso}T00:00:00+08:00`);
  const times = getSunTimes(point.latitude, point.longitude, date, {
    elevation: point.elevationMeters ?? 0,
    timezone: 8,
  });
  return {
    sunrise: times.sunrise,
    sunset: times.sunset,
    civilDawn: times.twilight?.civilDawn ?? null,
    nauticalDawn: times.twilight?.nauticalDawn ?? null,
    astronomicalDawn: times.twilight?.astronomicalDawn ?? null,
    solarNoon: times.solarNoon,
  };
}
