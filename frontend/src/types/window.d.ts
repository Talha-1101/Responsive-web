declare global {
  interface Window {
    appReady?: () => void;
  }
}

export {}