/**
 * apiFetch — a thin wrapper around fetch() that automatically injects
 * the Firebase ID token of the currently logged-in user as an
 * Authorization: Bearer <token> header.
 *
 * When deployed on Vercel, both frontend and backend are on the same domain,
 * so relative paths like `/api/chat` work out-of-the-box.
 *
 * For local development where backend runs on a different port (8000),
 * set VITE_API_URL=http://localhost:8000 in your .env file.
 *
 * Usage:
 *   import { apiFetch } from '../lib/apiFetch'
 *   const res = await apiFetch('/api/chat', { method: 'POST', body: JSON.stringify({...}) })
 */

import { auth } from './firebase'

// Base URL — empty string means same-origin (Vercel), or set VITE_API_URL for dev
const API_BASE = import.meta.env.VITE_API_URL || ''

/**
 * @param {string} url - The API endpoint path (e.g. '/api/chat')
 * @param {RequestInit} [options] - Standard fetch options
 * @returns {Promise<Response>}
 */
export async function apiFetch(url, options = {}) {
  const user = auth.currentUser
  let authHeader = {}

  if (user) {
    try {
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

  return fetch(`${API_BASE}${url}`, {
    ...options,
    headers: mergedHeaders,
  })
}

/**
 * Build a URL for endpoints that require auth via query param
 * (e.g. <video src> and EventSource — they can't send custom headers).
 * Returns a Promise<string>.
 */
export async function buildAuthUrl(path) {
  const user = auth.currentUser
  let token = ''
  if (user) {
    try {
      token = await user.getIdToken(false)
    } catch (e) {
      console.warn('buildAuthUrl: could not get token', e)
    }
  }
  const sep = path.includes('?') ? '&' : '?'
  return `${API_BASE}${path}${token ? `${sep}token=${encodeURIComponent(token)}` : ''}`
}
