/**
 * OIDC Authentication Module
 * Handles token acquisition and management from the OIDC provider
 */

interface OIDCConfig {
  providerUrl: string
  clientId: string
  redirectUri: string
  scope?: string
}

interface WellKnownConfig {
  authorization_endpoint: string
  token_endpoint: string
  jwks_uri: string
  userinfo_endpoint: string
  [key: string]: any
}

interface TokenResponse {
  access_token: string
  refresh_token?: string
  id_token?: string
  expires_in?: number
  [key: string]: any
}

export class OIDCClient {
  private providerUrl: string
  private clientId: string
  private redirectUri: string
  private scope: string
  private wellKnownUrl: string
  private wellKnown: WellKnownConfig | null = null

  constructor(config: OIDCConfig) {
    this.providerUrl = config.providerUrl
    this.clientId = config.clientId
    this.redirectUri = config.redirectUri
    this.scope = config.scope || 'openid profile email'
    this.wellKnownUrl = `${this.providerUrl.replace(/\/$/, '')}/.well-known/openid-configuration`
  }

  async fetchWellKnown(): Promise<WellKnownConfig> {
    if (this.wellKnown) return this.wellKnown

    const response = await fetch(this.wellKnownUrl)
    if (!response.ok) throw new Error('Failed to fetch well-known configuration')
    this.wellKnown = await response.json()
    return this.wellKnown as WellKnownConfig
  }

  async getAuthorizationUrl(): Promise<string> {
    const wellKnown = await this.fetchWellKnown()
    const state = this.generateRandomString(32)
    const codeVerifier = this.generateRandomString(43)
    const codeChallenge = await this.generateCodeChallenge(codeVerifier)

    sessionStorage.setItem('oidc_state', state)
    sessionStorage.setItem('oidc_code_verifier', codeVerifier)

    const params = new URLSearchParams({
      client_id: this.clientId,
      redirect_uri: this.redirectUri,
      response_type: 'code',
      scope: this.scope,
      state: state,
      code_challenge: codeChallenge,
      code_challenge_method: 'S256'
    })

    return `${wellKnown.authorization_endpoint}?${params.toString()}`
  }

  async exchangeCodeForToken(code: string): Promise<TokenResponse> {
    const wellKnown = await this.fetchWellKnown()
    const codeVerifier = sessionStorage.getItem('oidc_code_verifier')

    if (!codeVerifier) {
      throw new Error('Code verifier not found. Session may have expired.')
    }

    const response = await fetch(wellKnown.token_endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        grant_type: 'authorization_code',
        client_id: this.clientId,
        code: code,
        redirect_uri: this.redirectUri,
        code_verifier: codeVerifier
      }).toString()
    })

    if (!response.ok) {
      throw new Error('Failed to exchange code for token')
    }

    const tokenResponse: TokenResponse = await response.json()
    sessionStorage.removeItem('oidc_code_verifier')
    return tokenResponse
  }

  private generateRandomString(length: number): string {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~'
    let result = ''
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    return result
  }

  private async generateCodeChallenge(codeVerifier: string): Promise<string> {
    const encoder = new TextEncoder()
    const data = encoder.encode(codeVerifier)
    const hash = await crypto.subtle.digest('SHA-256', data)
    return this.base64UrlEncode(hash)
  }

  private base64UrlEncode(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer)
    let binary = ''
    for (let i = 0; i < bytes.length; i++) {
      binary += String.fromCharCode(bytes[i])
    }
    return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '')
  }

  decodeToken(token: string): Record<string, any> {
    const parts = token.split('.')
    if (parts.length !== 3) throw new Error('Invalid token')

    const payload = parts[1]
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'))
    return JSON.parse(decoded)
  }

  isTokenExpired(token: string): boolean {
    try {
      const payload = this.decodeToken(token)
      if (!payload.exp) return false
      return Date.now() >= payload.exp * 1000
    } catch {
      return true
    }
  }
}

export class AuthManager {
  private oidcClient: OIDCClient
  private readonly tokenKey = 'oidc_access_token'
  private readonly refreshTokenKey = 'oidc_refresh_token'
  private readonly idTokenKey = 'oidc_id_token'

  constructor(oidcClient: OIDCClient) {
    this.oidcClient = oidcClient
  }

  async login(): Promise<void> {
    const authUrl = await this.oidcClient.getAuthorizationUrl()
    window.location.href = authUrl
  }

  async handleCallback(code: string): Promise<void> {
    const tokenResponse = await this.oidcClient.exchangeCodeForToken(code)
    this.setToken(tokenResponse.access_token)
    if (tokenResponse.refresh_token) {
      this.setRefreshToken(tokenResponse.refresh_token)
    }
    if (tokenResponse.id_token) {
      this.setIdToken(tokenResponse.id_token)
    }
  }

  logout(): void {
    sessionStorage.removeItem(this.tokenKey)
    sessionStorage.removeItem(this.refreshTokenKey)
    sessionStorage.removeItem(this.idTokenKey)
    sessionStorage.removeItem('oidc_state')
  }

  setToken(token: string): void {
    sessionStorage.setItem(this.tokenKey, token)
  }

  getToken(): string | null {
    return sessionStorage.getItem(this.tokenKey)
  }

  setRefreshToken(token: string): void {
    sessionStorage.setItem(this.refreshTokenKey, token)
  }

  getRefreshToken(): string | null {
    return sessionStorage.getItem(this.refreshTokenKey)
  }

  setIdToken(token: string): void {
    sessionStorage.setItem(this.idTokenKey, token)
  }

  getIdToken(): string | null {
    return sessionStorage.getItem(this.idTokenKey)
  }

  isAuthenticated(): boolean {
    const token = this.getToken()
    if (!token) return false
    return !this.oidcClient.isTokenExpired(token)
  }

  getUser(): Record<string, any> | null {
    const idToken = this.getIdToken()
    if (!idToken) return null
    try {
      return this.oidcClient.decodeToken(idToken)
    } catch {
      return null
    }
  }
}
