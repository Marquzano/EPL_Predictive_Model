import type { TeamResponse } from '../api/types'

type TeamSelectProps = {
    label: string
    teams: TeamResponse[]
    value: number | null
    onChange: (teamId: number) => void
}

export function TeamSelect({ label, teams, value, onChange }: TeamSelectProps) {
    return (
        <label>
            {label}
            <select
                value={value ?? ''}
                onChange={(event) => onChange(Number(event.target.value))}
            >
                <option value="" disabled>
                    Select a team
                </option>
                {teams.map((team) => (
                    <option key={team.team_id} value={team.team_id}>
                        {team.team}
                    </option>
                ))}
            </select>
        </label>
    )
}