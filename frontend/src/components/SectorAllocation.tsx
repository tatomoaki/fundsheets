import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface Sector {
  name: string
  value: number
  color: string
}

const SECTORS: Sector[] = [
  { name: 'Financials', value: 29, color: '#2563eb' },
  { name: 'Industrials', value: 23, color: '#0ea5e9' },
  { name: 'Resources',   value: 23, color: '#14b8a6' },
  { name: 'Consumer',    value: 22, color: '#f59e0b' },
  { name: 'Technology',  value: 3,  color: '#8b5cf6' },
]

export function SectorAllocation() {
  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold text-gray-700">Sector Allocation</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4">
          <div className="w-36 h-36 shrink-0">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={SECTORS}
                  cx="50%"
                  cy="50%"
                  innerRadius={36}
                  outerRadius={62}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {SECTORS.map((sector) => (
                    <Cell key={sector.name} fill={sector.color} stroke="none" />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value: number) => [`${value}%`, '']}
                  contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid #e5e7eb' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="flex flex-col gap-2 flex-1 min-w-0">
            {SECTORS.map((sector) => (
              <div key={sector.name} className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-1.5 min-w-0">
                  <span className="size-2.5 rounded-full shrink-0" style={{ backgroundColor: sector.color }} />
                  <span className="text-xs text-gray-600 truncate">{sector.name}</span>
                </div>
                <span className="text-xs font-semibold text-gray-800 shrink-0">{sector.value}%</span>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
