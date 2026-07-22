import { TrendingDown, TrendingUp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const DATA = {
  totalValue: 2450000,
  correlationOverlap: 16.3,
  maximumDrawdown: -8.4,
}

function formatCurrency(value: number) {
  return `R ${value.toLocaleString('en-ZA')}`
}

export function PortfolioOverview() {
  const drawdownPositive = DATA.maximumDrawdown >= 0

  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold text-gray-700">Total Portfolio Overview</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <p className="text-3xl font-bold text-gray-900 tracking-tight">
            {formatCurrency(DATA.totalValue)}
          </p>
          <p className="text-xs text-gray-500 mt-0.5">Total Investments</p>
        </div>

        <div className="flex items-start gap-4">
          <div className="flex-1 bg-gray-50 rounded-lg p-3">
            <p className="text-xl font-bold text-blue-600">{DATA.correlationOverlap}%</p>
            <p className="text-xs text-gray-500 mt-0.5">Correlation Overlap</p>
          </div>

          <div className="flex-1 bg-gray-50 rounded-lg p-3">
            <div className="flex items-center gap-1">
              {drawdownPositive
                ? <TrendingUp className="size-4 text-emerald-500" />
                : <TrendingDown className="size-4 text-red-500" />
              }
              <p className={`text-xl font-bold ${drawdownPositive ? 'text-emerald-600' : 'text-red-600'}`}>
                {DATA.maximumDrawdown}%
              </p>
            </div>
            <p className="text-xs text-gray-500 mt-0.5">Maximum Drawdown</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
