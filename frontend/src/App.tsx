import { useEffect, useState } from 'react'
import { getTeams } from './api/client'
import type { TeamResponse } from './api/types'
import { TeamSelect } from './components/TeamSelect'

function App() {
  const [teams, setTeams] = useState<TeamResponse[]>([])
  const [homeId, setHomeId] = useState<number | null>(null)
  const [awayId, setAwayId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

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

  return (
    <main>
      <h1>EPL Predictor</h1>
      {error && <p>Could not load teams: {error}</p>}
      <TeamSelect label="Home" teams={teams} value={homeId} onChange={setHomeId} />
      <TeamSelect label="Away" teams={teams} value={awayId} onChange={setAwayId} />
      <p>
        Selected: home={homeId ?? 'none'}, away={awayId ?? 'none'}
      </p>
    </main>
  )
}

export default App
