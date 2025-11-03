/**
 * Browser capability detection utilities
 * Used for conditional feature loading and fallbacks
 */

export function canUseWebGL(): boolean {
  try {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    return !!gl;
  } catch (e) {
    return false;
  }
}

export function canUseWebWorkers(): boolean {
  return typeof Worker !== 'undefined';
}

export function canUseIndexedDB(): boolean {
  return typeof indexedDB !== 'undefined';
}

export function canUseLocalStorage(): boolean {
  try {
    const test = '__test__';
    localStorage.setItem(test, test);
    localStorage.removeItem(test);
    return true;
  } catch (e) {
    return false;
  }
}