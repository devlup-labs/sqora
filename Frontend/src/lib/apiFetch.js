/**
 * apiFetch — a thin wrapper around fetch() that automatically injects
 * the Firebase ID token of the currently logged-in user as an
 * Authorization: Bearer <token> header.
 *
 * Firebase caches the token and refreshes it automatically, so calling
 * getIdToken() is cheap (no network round-trip unless the token has expired).
 *
 * Usage:
 *   import { apiFetch } from '../lib/apiFetch'
 *   const res = await apiFetch('/api/chat', { method: 'POST', body: JSON.stringify({...}) })
 */

import { auth } from './firebase'

/**
 * @param {string} url - The API endpoint path
 * @param {RequestInit} [options] - Standard fetch options (method, body, headers, etc.)
 * @returns {Promise<Response>}
 */
export async function apiFetch(url, options = {}) {
  const user = auth.currentUser
  let authHeader = {}

  if (user) {
    try {
      // forceRefresh=false: uses cached token, refreshes only if expiring soon
      const token = await user.getIdToken(false)
      authHeader = { Authorization: `Bearer ${token}` }
    } catch (err) {
      console.warn('apiFetch: could not get ID token', err)
    }
  }

  const mergedHeaders = {
    'Content-Type': 'application/json',
    ...authHeader,
    ...(options.headers || {}),
  }

  return fetch(url, {
    ...options,
    headers: mergedHeaders,
  })
}
