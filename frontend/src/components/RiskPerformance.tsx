import { useState } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'

const PERIODS = ['1Y', '3Y', '5Y'] as const
type Period = typeof PERIODS[number]

const CHART_DATA: Record<Period, { month: string; afterGray: number; generation: number; moneyMax: number }[]> = {
  '1Y': [
    { month: 'Jan', afterGray: -2.1, generation: -1.5, moneyMax: -3.2 },
    { month: 'Feb', afterGray: -3.4, generation: -2.8, moneyMax: -4.5 },
    { month: 'Mar', afterGray: -1.8, generation: -1.2, moneyMax: -2.9 },
    { month: 'Apr', afterGray: -4.2, generation: -3.1, moneyMax: -5.8 },
    { month: 'May', afterGray: -2.5, generation: -2.0, moneyMax: -3.5 },
    { month: 'Jun', afterGray: -1.1, generation: -0.8, moneyMax: -1.9 },
    { month: 'Jul', afterGray: -0.5, generation: -0.3, moneyMax: -1.0 },
    { month: 'Aug', afterGray:  0.8, generation:  1.2, moneyMax:  0.3 },
    { month: 'Sep', afterGray: -1.3, generation: -0.9, moneyMax: -2.1 },
    { month: 'Oct', afterGray: -2.8, generation: -2.1, moneyMax: -3.9 },
    { month: 'Nov', afterGray: -3.5, generation: -2.7, moneyMax: -4.8 },
    { month: 'Dec', afterGray: -1.4, generation: -1.0, moneyMax: -2.2 },
  ],
  '3Y': [
    { month: 'Q1 22', afterGray: -3.2, generation: -2.5, moneyMax: -4.1 },
    { month: 'Q2 22', afterGray: -5.8, generation: -4.2, moneyMax: -7.3 },
    { month: 'Q3 22', afterGray: -4.1, generation: -3.0, moneyMax: -5.5 },
    { month: 'Q4 22', afterGray: -2.0, generation: -1.5, moneyMax: -2.9 },
    { month: 'Q1 23', afterGray: -1.5, generation: -1.1, moneyMax: -2.2 },
    { month: 'Q2 23', afterGray: -0.8, generation: -0.4, moneyMax: -1.3 },
    { month: 'Q3 23', afterGray: -2.3, generation: -1.8, moneyMax: -3.4 },
    { month: 'Q4 23', afterGray: -1.1, generation: -0.7, moneyMax: -1.8 },
    { month: 'Q1 24', afterGray: -3.5, generation: -2.6, moneyMax: -4.7 },
    { month: 'Q2 24', afterGray: -1.4, generation: -1.0, moneyMax: -2.2 },
    { month: 'Q3 24', afterGray: -0.6, generation: -0.2, moneyMax: -1.1 },
    { month: 'Q4 24', afterGray: -1.4, generation: -1.0, moneyMax: -2.2 },
  ],
  '5Y': [
    { month: '2020', afterGray: -8.2, generation: -6.5, moneyMax: -11.3 },
    { month: '2021', afterGray: -2.1, generation: -1.4, moneyMax: -3.2  },
    { month: '2022', afterGray: -5.8, generation: -4.2, moneyMax: -7.3  },
    { month: '2023', afterGray: -1.5, generation: -1.1, moneyMax: -2.2  },
    { month: '2024', afterGray: -3.5, generation: -2.6, moneyMax: -4.7  },
  ],
}

const VOLATILITY = [
  { name: 'After Gray Balanced Fund', volatility: 12.34, correlation: 0.87 },
  { name: 'Money Max Managed',        volatility: 12.31, correlation: 0.87 },
  { name: 'Generation Equity Fund',   volatility: 14.05, correlation: 0.76 },
]

const LINES = [
  { key: 'afterGray', color: '#4f46e5', label: 'After Gray Balanced' },
  { key: 'generation', color: '#0ea5e9', label: 'Generation Equity' },
  { key: 'moneyMax',  color: '#f59e0b', label: 'Money Max Managed' },
] as const

export function RiskPerformance() {
  const [period, setPeriod] = useState<Period>('1Y')

  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-semibold text-gray-700">Risk & Performance Comparison</CardTitle>
          <div className="flex gap-1">
            {PERIODS.map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={cn(
                  'px-2 py-0.5 text-xs rounded font-medium transition-colors',
                  period === p
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                )}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div>
          <p className="text-xs font-medium text-gray-500 mb-2">Historical Drawdown</p>
          <ResponsiveContainer width="100%" height={130}>
            <LineChart data={CHART_DATA[period]} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <ReferenceLine y={0} stroke="#9ca3af" strokeWidth={1} />
              <XAxis dataKey="month" tick={{ fontSize: 9, fill: '#9ca3af' }} tickLine={false} axisLine={false} />
              <YAxis tick={{ fontSize: 9, fill: '#9ca3af' }} tickLine={false} axisLine={false} tickFormatter={(v) => `${v}%`} />
              <Tooltip
                formatter={(value: number, name: string) => [`${value.toFixed(1)}%`, name]}
                contentStyle={{ fontSize: 11, borderRadius: 6, border: '1px solid #e5e7eb' }}
              />
              {LINES.map((l) => (
                <Line
                  key={l.key}
                  type="monotone"
                  dataKey={l.key}
                  name={l.label}
                  stroke={l.color}
                  strokeWidth={1.8}
                  dot={false}
                  activeDot={{ r: 3 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap gap-x-4 gap-y-1 mt-1">
            {LINES.map((l) => (
              <div key={l.key} className="flex items-center gap-1.5">
                <span className="size-2.5 rounded-full shrink-0" style={{ backgroundColor: l.color }} />
                <span className="text-[10px] text-gray-500">{l.label}</span>
              </div>
            ))}
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-medium text-gray-500">Volatility & Correlation</p>
            <span className="text-xs font-bold text-blue-600">3.3%</span>
          </div>
          <div className="border rounded-md overflow-hidden text-xs">
            <table className="w-full">
              <thead>
                <tr className="bg-gray-50 border-b">
                  <th className="text-left px-3 py-1.5 font-semibold text-gray-600">Fund</th>
                  <th className="text-right px-3 py-1.5 font-semibold text-gray-600">Volatility</th>
                  <th className="text-right px-3 py-1.5 font-semibold text-gray-600">Correlation</th>
                </tr>
              </thead>
              <tbody>
                {VOLATILITY.map((row) => (
                  <tr key={row.name} className="border-b last:border-0 hover:bg-gray-50">
                    <td className="px-3 py-1.5 text-gray-700 max-w-[120px] truncate">{row.name}</td>
                    <td className="px-3 py-1.5 text-right text-gray-800 font-medium tabular-nums">{row.volatility.toFixed(2)}</td>
                    <td className="px-3 py-1.5 text-right text-gray-800 font-medium tabular-nums">{row.correlation.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
