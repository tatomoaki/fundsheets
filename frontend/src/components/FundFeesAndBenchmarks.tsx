import { ExternalLink } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface FundFee {
  name: string
  benchmark: string
  ter: number
  oneYear: number
  threeYear: number
}

const FUNDS: FundFee[] = [
  { name: 'After Gray Balanced Fund', benchmark: 'FTSE/JSE All Share Index', ter: 1.23, oneYear: 14.5, threeYear: 15.2 },
  { name: 'Generation Equity Fund',   benchmark: 'FTSE/JSE All Share Index', ter: 1.50, oneYear: 14.5, threeYear: 15.2 },
  { name: 'FTSE/JSE All Share Index', benchmark: 'FTSE/JSE Top Cap Index',   ter: 1.50, oneYear: 13.1, threeYear: 14.0 },
  { name: 'FTSE/JSE Cap Index',       benchmark: 'FTSE/JSE Cap Index',       ter: 1.50, oneYear: 11.2, threeYear: 12.4 },
]

function PerfCell({ value }: { value: number }) {
  const positive = value >= 0
  return (
    <td className={`px-3 py-2 text-right font-medium tabular-nums ${positive ? 'text-emerald-600' : 'text-red-500'}`}>
      {positive ? '+' : ''}{value.toFixed(1)}%
    </td>
  )
}

export function FundFeesAndBenchmarks() {
  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold text-gray-700">Fund Fees & Benchmarks</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="border rounded-md overflow-hidden text-xs">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b">
                <th className="text-left px-3 py-2 font-semibold text-gray-600">Fund</th>
                <th className="text-left px-3 py-2 font-semibold text-gray-600 hidden sm:table-cell">Benchmark</th>
                <th className="text-right px-3 py-2 font-semibold text-gray-600">TER</th>
                <th className="text-right px-3 py-2 font-semibold text-gray-600">1yr</th>
                <th className="text-right px-3 py-2 font-semibold text-gray-600">3yr</th>
              </tr>
            </thead>
            <tbody>
              {FUNDS.map((fund) => (
                <tr key={fund.name} className="border-b last:border-0 hover:bg-gray-50 transition-colors">
                  <td className="px-3 py-2 text-gray-800 font-medium max-w-[110px] truncate">{fund.name}</td>
                  <td className="px-3 py-2 text-gray-500 max-w-[100px] truncate hidden sm:table-cell">{fund.benchmark}</td>
                  <td className="px-3 py-2 text-right text-gray-700 tabular-nums">{fund.ter.toFixed(2)}%</td>
                  <PerfCell value={fund.oneYear} />
                  <PerfCell value={fund.threeYear} />
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <button className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 font-medium transition-colors">
          View Full Details
          <ExternalLink className="size-3" />
        </button>
      </CardContent>
    </Card>
  )
}
