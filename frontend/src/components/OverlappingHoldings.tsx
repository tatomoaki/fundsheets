import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export interface OverlapHolding {
  name: string
  overlap: number
}

interface Props {
  holdings: OverlapHolding[]
}

export function OverlappingHoldings({ holdings }: Props) {
  const max = holdings[0]?.overlap ?? 1

  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-semibold text-gray-700">Top Overlapping Holdings</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {holdings.length === 0 ? (
          <p className="text-xs text-gray-400">No holdings in common.</p>
        ) : (
          holdings.map((holding) => (
            <div key={holding.name} className="space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-600 truncate pr-4">{holding.name}</span>
                <span className="text-xs font-semibold text-gray-800 shrink-0">{holding.overlap.toFixed(2)}%</span>
              </div>
              <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-teal-500 rounded-full transition-all duration-500"
                  style={{ width: `${(holding.overlap / max) * 100}%` }}
                />
              </div>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  )
}
