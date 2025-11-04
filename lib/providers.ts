import type { Envelope } from "./types"

export interface EnvelopeProvider {
  load(): Promise<Envelope>
}

export class FileProvider implements EnvelopeProvider {
  constructor(private file?: File) {}

  async load(): Promise<Envelope> {
    if (!this.file) {
      throw new Error("No file provided")
    }
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const json = JSON.parse(e.target?.result as string)
          resolve(json as Envelope)
        } catch (err) {
          reject(new Error("Failed to parse JSON"))
        }
      }
      reader.onerror = () => reject(new Error("Failed to read file"))
      reader.readAsText(this.file)
    })
  }
}

export class DevHTTPProvider implements EnvelopeProvider {
  constructor(private url = "/envelope.json") {}

  async load(): Promise<Envelope> {
    const response = await fetch(this.url)
    if (!response.ok) {
      throw new Error(`Failed to fetch: ${response.status}`)
    }
    return response.json() as Promise<Envelope>
  }
}
