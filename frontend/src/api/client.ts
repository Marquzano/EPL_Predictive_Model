import type { TeamResponse } from './types'

const API_BASE = 'http://localhost:8000'

export async function getTeams(): Promise<TeamResponse[]> {
    const response = await fetch(`${API_BASE}/teams`)
    if (!response.ok) {
        throw new Error(`GET /teams failed: ${response.status}`)
    }
    return response.json()
}