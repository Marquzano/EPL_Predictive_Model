import type { PredictRequest, PredictResponse, TeamResponse } from './types'

const API_BASE = 'http://localhost:8000'

export async function getTeams(): Promise<TeamResponse[]> {
    const response = await fetch(`${API_BASE}/teams`)
    if (!response.ok) {
        throw new Error(`GET /teams failed: ${response.status}`)
    }
    return response.json()
}

export async function predictMatch(request: PredictRequest): Promise<PredictResponse> {
    const response = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json' },
        body: JSON.stringify(request),
    })
    if (!response.ok) {
        throw new Error(`POST /predict failed: ${response.status}`)
    }
    return response.json()
}