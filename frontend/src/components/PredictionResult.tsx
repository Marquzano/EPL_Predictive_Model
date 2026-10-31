import type { PredictResponse } from '../api/types'

type PredictResultProps = {
    prediction: PredictResponse
    homeName: string
    awayName: string
}

function formatPercent(probability: number): string {
    return `${(probability * 100).toFixed(1)}%`
}

export function PredictionResult({ prediction, homeName, awayName }: PredictResultProps) {
    return (
        <ul>
            <li>{homeName} win: {formatPercent(prediction.home_win_probability)}</li>
            <li>Draw: {formatPercent(prediction.draw_probability)}</li>
            <li>{awayName} win: {formatPercent(prediction.away_win_probability)}</li>
        </ul>
    )
}