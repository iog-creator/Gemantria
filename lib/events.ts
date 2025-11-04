type EventListener = (...args: any[]) => void

export class EventBus {
  private listeners: Map<string, EventListener[]> = new Map()

  on(event: string, listener: EventListener) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event)!.push(listener)
  }

  off(event: string, listener: EventListener) {
    const eventListeners = this.listeners.get(event)
    if (eventListeners) {
      const index = eventListeners.indexOf(listener)
      if (index > -1) eventListeners.splice(index, 1)
    }
  }

  emit(event: string, ...args: any[]) {
    const eventListeners = this.listeners.get(event)
    if (eventListeners) {
      eventListeners.forEach((listener) => listener(...args))
    }
  }
}
