import { useEffect, useState } from 'react'
import { getTeams, predictMatch } from './api/client'
import type { PredictResponse, TeamResponse } from './api/types'
import { PredictionResult } from './components/PredictionResult'
import { TeamSelect } from './components/TeamSelect'

function App() {
  const [teams, setTeams] = useState<TeamResponse[]>([])
  const [homeId, setHomeId] = useState<number | null>(null)
  const [awayId, setAwayId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [prediction, setPrediction] = useState<PredictResponse | null>(null) // does the null need to be there?
  const [isPredicting, setIsPredicting] = useState(false)
  const [predictError, setPredictError] = useState<string | null>(null)

  useEffect(() => {
    let ignore = false

    getTeams()
      .then((data) => {
        if (!ignore) setTeams(data)
      })
      .catch((err: Error) => {
        if (!ignore) setError(err.message)
      })

    return () => {
      ignore = true
    }
  }, [])

  function handleHomeChange(teamId: number) {
    setHomeId(teamId)
    setPrediction(null)
  }

  function handleAwayChange(teamId: number) {
    setAwayId(teamId)
    setPrediction(null)
  }

  async function handlePredict() {
    if (homeId === null || awayId === null) return
    
    setIsPredicting(true)
    setPredictError(null)
    try {
      const result = await predictMatch({ home_team_id: homeId, away_team_id: awayId })
      setPrediction(result)
    } catch (err) {
      setPredictError(err instanceof Error ? err.message : String(err))
    } finally {
      setIsPredicting(false)
    }
  }

  const homeName = teams.find((team) => team.team_id === homeId)?.team ?? 'Home'
  const awayName = teams.find((team) => team.team_id === awayId)?.team ?? 'Away'
  const canPredict = homeId !== null && awayId !== null && homeId !== awayId && !isPredicting

  return (
    <main>
      <h1>EPL Predictor</h1>
      {error && <p>Could not load teams: {error}</p>}
      <TeamSelect label="Home" teams={teams} value={homeId} onChange={handleHomeChange} />
      <TeamSelect label="Away" teams={teams} value={awayId} onChange={handleAwayChange} />
      { homeId !== null && homeId === awayId && <p>Pick two different teams.</p>}
      <button type="button" onClick={handlePredict} disabled={!canPredict}>
        {isPredicting ? 'Predicting...' : 'Predict'}
      </button>
      {predictError && <p>Prediction failed: {predictError}</p>}
      {prediction && (
        <PredictionResult prediction={prediction} homeName={homeName} awayName={awayName} />
      )}
      {/* <p>
        Selected: home={homeId ?? 'none'}, away={awayId ?? 'none'}
      </p> */}
    </main>
  )
}

export default App
