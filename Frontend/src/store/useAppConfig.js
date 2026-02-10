import { create } from 'zustand'

const STORAGE_KEY = 'sqora_app_config'

const defaultConfig = {
  mentorGreeting:
    'Hi! I am your AI mentor. Tap the mic or open chat to ask anything about your prep.',
  voiceEnabled: true,
}

const loadInitialConfig = () => {
  if (typeof window === 'undefined') return defaultConfig
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return defaultConfig
    const parsed = JSON.parse(raw)
    return { ...defaultConfig, ...parsed }
  } catch {
    return defaultConfig
  }
}

const persistConfig = (config) => {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(config))
  } catch {
    // ignore
  }
}

export const useAppConfig = create((set, get) => ({
  ...loadInitialConfig(),

  setMentorGreeting: (mentorGreeting) => {
    const next = { ...get(), mentorGreeting }
    set({ mentorGreeting })
    persistConfig(next)
  },

  setVoiceEnabled: (voiceEnabled) => {
    const next = { ...get(), voiceEnabled }
    set({ voiceEnabled })
    persistConfig(next)
  },
}))

