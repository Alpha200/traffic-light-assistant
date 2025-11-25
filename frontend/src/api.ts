import type { AuthManager } from './auth'

export class ApiClient {
  private baseUrl: string
  private authManager: AuthManager | null = null

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl || window.location.origin
  }

  setAuthManager(authManager: AuthManager): void {
    this.authManager = authManager
  }

  private async request<T>(
    method: string,
    endpoint: string,
    body?: Record<string, any>
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    }

    // Add authorization header if available
    if (this.authManager) {
      const token = this.authManager.getToken()
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }
    }

    const response = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined
    })

    // Handle 401 Unauthorized
    if (response.status === 401) {
      if (this.authManager) {
        this.authManager.logout()
      }
      window.location.href = '/callback'
      throw new Error('Unauthorized')
    }

    if (!response.ok) {
      const errorData = await response.text()
      throw new Error(`HTTP ${response.status}: ${errorData}`)
    }

    if (response.status === 204) {
      return undefined as T
    }

    return await response.json()
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>('GET', endpoint)
  }

  async post<T>(endpoint: string, body: Record<string, any>): Promise<T> {
    return this.request<T>('POST', endpoint, body)
  }

  async put<T>(endpoint: string, body: Record<string, any>): Promise<T> {
    return this.request<T>('PUT', endpoint, body)
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>('DELETE', endpoint)
  }
}
