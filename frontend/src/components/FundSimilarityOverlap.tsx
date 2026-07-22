import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export interface FundEntry {
  label: string
  name: string
  color: string
}

export interface OverlapPair {
  fundA: string
  fundB: string
  overlap: number
}

interface Props {
  funds: FundEntry[]
  pairs: OverlapPair[]
}

// Positions for up to 4 funds in a Venn-style layout
const CIRCLE_POSITIONS: { cx: number; cy: number; labelX: number; labelY: number }[] = [
  { cx: 80,  cy: 72,  labelX: 48,  labelY: 52  }, // top-left
  { cx: 120, cy: 72,  labelX: 152, labelY: 52  }, // top-right
  { cx: 100, cy: 108, labelX: 100, labelY: 158 }, // bottom
  { cx: 100, cy: 72,  labelX: 100, labelY: 30  }, // top-center (4th)
]

function VennDiagram({ funds }: { funds: FundEntry[] }) {
  const count = Math.min(funds.length, 3)
  const circles = CIRCLE_POSITIONS.slice(0, count)

  return (
    <svg viewBox="0 0 200 170" className="w-full h-36">
      {circles.map((pos, i) => (
        <circle
          key={funds[i].label}
          cx={pos.cx}
          cy={pos.cy}
          r={52}
          fill={funds[i].color}
          fillOpacity={0.25}
          stroke={funds[i].color}
          strokeWidth={1.5}
          strokeOpacity={0.6}
        />
      ))}
      {circles.map((pos, i) => (
        <text
          key={funds[i].label}
          x={pos.labelX}
          y={pos.labelY}
          textAnchor="middle"
          fill={funds[i].color}
          fontSize={9}
          fontWeight={700}
        >
          {funds[i].label}
        </text>
      ))}
      <text x="100" y="92" textAnchor="middle" fill="#374151" fontSize={8.5} fontWeight={600}>
        Overlap
      </text>
    </svg>
  )
}

export function FundSimilarityOverlap({ funds, pairs }: Props) {
  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold text-gray-700">Fund Similarity & Overlap</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {funds.length >= 2 && (
          <div>
            <p className="text-xs font-medium text-gray-500 mb-1">Overall Holdings Overlap</p>
            <VennDiagram funds={funds} />
          </div>
        )}

        <div className="border rounded-md overflow-hidden text-xs">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b">
                <th className="text-left px-3 py-2 font-semibold text-gray-600">Fund A</th>
                <th className="text-left px-3 py-2 font-semibold text-gray-600">Fund B</th>
                <th className="text-right px-3 py-2 font-semibold text-gray-600">Overlap %</th>
              </tr>
            </thead>
            <tbody>
              {pairs.length === 0 ? (
                <tr>
                  <td colSpan={3} className="px-3 py-3 text-center text-gray-400">No data</td>
                </tr>
              ) : (
                pairs.map((pair) => (
                  <tr key={`${pair.fundA}-${pair.fundB}`} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="px-3 py-2 text-gray-700 truncate max-w-[100px]">{pair.fundA}</td>
                    <td className="px-3 py-2 text-gray-700 truncate max-w-[100px]">{pair.fundB}</td>
                    <td className="px-3 py-2 text-right font-semibold text-blue-600">{pair.overlap.toFixed(1)}%</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="flex flex-col gap-1.5">
          {funds.map((f) => (
            <div key={f.label} className="flex items-center gap-2">
              <span className="size-2.5 rounded-full shrink-0" style={{ backgroundColor: f.color }} />
              <span className="text-xs text-gray-500">
                <span className="font-semibold text-gray-700">{f.label}:</span> {f.name}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
