import { useEffect, useState } from 'react'
import { ChevronLeft } from 'lucide-react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface Fund {
  id: string
  name: string
  manager: string | null
  risk_profile: string | null
  asisa_classification: string | null
  benchmark: string | null
  portfolio_launch_date: string | null
  portfolio_size: string | null
  as_of_date: string | null
}

interface Holding {
  id: string
  instrument_name: string
  weight_pct: number | null
  as_of_date: string
}

interface AssetAllocation {
  id: string
  asset_class: string
  weight_pct: number | null
  as_of_date: string
}

interface Fee {
  id: string
  advice_initial_fee_max_pct: number | null
  manager_initial_fee_pct: number | null
  advice_annual_fee_max_pct: number | null
  manager_annual_fee_pct: number | null
  ter: number | null
  transaction_cost_pct: number | null
  total_investment_charge_pct: number | null
  currency: string
  effective_date: string
}

interface PerformanceRecord {
  id: string
  period: string
  fund_return_pct: number | null
  benchmark_return_pct: number | null
  tracking_difference_pct: number | null
  as_of_date: string | null
}

interface AnnualReturns {
  id: string
  highest_pct: number | null
  lowest_pct: number | null
  as_of_date: string
}

interface FundSheetPageProps {
  fund: Fund
  onBack: () => void
}

const CHART_COLORS = [
  '#2563eb', '#0ea5e9', '#14b8a6', '#f59e0b', '#8b5cf6',
  '#ec4899', '#10b981', '#f97316', '#6366f1', '#84cc16',
  '#06b6d4', '#a855f7',
]

const PERIOD_ORDER = ['1 year', '3 year', '5 year', '7 year', '10 year', 'Launch']

function fmt(value: number | null, decimals = 2): string {
  if (value == null) return '—'
  return `${Number(value).toFixed(decimals)}%`
}

function FeeRow({ label, value }: { label: string; value: number | null }) {
  if (value == null) return null
  return (
    <div className="flex justify-between text-xs py-1 border-b border-gray-50 last:border-0">
      <span className="text-gray-500">{label}</span>
      <span className="font-semibold text-gray-800">{fmt(value)}</span>
    </div>
  )
}

function InfoRow({ label, value }: { label: string; value: string | null | undefined }) {
  if (!value) return null
  return (
    <div className="flex justify-between text-xs py-1 border-b border-gray-50 last:border-0">
      <span className="text-gray-500">{label}</span>
      <span className="font-medium text-gray-800 text-right max-w-[60%]">{value}</span>
    </div>
  )
}

export function FundSheetPage({ fund, onBack }: FundSheetPageProps) {
  const [holdings, setHoldings] = useState<Holding[]>([])
  const [allocations, setAllocations] = useState<AssetAllocation[]>([])
  const [fee, setFee] = useState<Fee | null>(null)
  const [performance, setPerformance] = useState<PerformanceRecord[]>([])
  const [annualReturns, setAnnualReturns] = useState<AnnualReturns | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    Promise.all([
      fetch(`/api/funds/${fund.id}/holdings`).then(r => r.ok ? r.json() : []),
      fetch(`/api/funds/${fund.id}/asset-allocations`).then(r => r.ok ? r.json() : []),
      fetch(`/api/funds/${fund.id}/fees/latest`).then(r => r.ok ? r.json() : null),
      fetch(`/api/funds/${fund.id}/performance`).then(r => r.ok ? r.json() : []),
      fetch(`/api/funds/${fund.id}/performance/annual-returns`).then(r => r.ok ? r.json() : null),
    ]).then(([h, a, f, p, ar]) => {
      setHoldings(h)
      setAllocations(a)
      setFee(f)
      setPerformance(
        [...p].sort((x: PerformanceRecord, y: PerformanceRecord) =>
          PERIOD_ORDER.indexOf(x.period) - PERIOD_ORDER.indexOf(y.period)
        )
      )
      setAnnualReturns(ar)
    }).finally(() => setLoading(false))
  }, [fund.id])

  const allocationData = allocations.map((a, i) => ({
    name: a.asset_class,
    value: Number(a.weight_pct ?? 0),
    color: CHART_COLORS[i % CHART_COLORS.length],
  }))

  const asOfDate = holdings[0]?.as_of_date ?? allocations[0]?.as_of_date ?? fund.as_of_date

  return (
    <div className="p-5 space-y-5">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <button
            onClick={onBack}
            className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 mb-2 cursor-pointer"
          >
            <ChevronLeft className="size-3.5" /> Back to Funds
          </button>
          <h1 className="text-xl font-bold text-gray-900">{fund.name}</h1>
          <p className="text-sm text-gray-500 mt-0.5">{fund.manager}</p>
          {fund.asisa_classification && (
            <p className="text-xs text-gray-400 mt-0.5">{fund.asisa_classification}</p>
          )}
        </div>
        <div className="text-right shrink-0">
          {fund.risk_profile && (
            <span className="inline-block text-xs font-medium px-2 py-0.5 rounded-full bg-orange-100 text-orange-700 mb-1">
              {fund.risk_profile}
            </span>
          )}
          {asOfDate && (
            <p className="text-xs text-gray-400">
              As of {new Date(asOfDate).toLocaleDateString('en-ZA', { year: 'numeric', month: 'long', day: 'numeric' })}
            </p>
          )}
        </div>
      </div>

      {loading ? (
        <div className="text-sm text-gray-400">Loading fund data…</div>
      ) : (
        <div className="space-y-4">

          {/* Row 1: Asset Allocation | Top Holdings | Fund Info */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

            {/* Asset Allocation */}
            <Card className="h-full">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold text-gray-700">Asset Allocation</CardTitle>
              </CardHeader>
              <CardContent>
                {allocationData.length === 0 ? (
                  <p className="text-xs text-gray-400">No allocation data</p>
                ) : (
                  <div className="flex flex-col gap-3">
                    <div className="h-44">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={allocationData}
                            cx="50%"
                            cy="50%"
                            innerRadius={45}
                            outerRadius={75}
                            paddingAngle={2}
                            dataKey="value"
                          >
                            {allocationData.map((entry) => (
                              <Cell key={entry.name} fill={entry.color} stroke="none" />
                            ))}
                          </Pie>
                          <Tooltip
                            formatter={(value: number) => [`${value}%`, '']}
                            contentStyle={{ fontSize: 12, borderRadius: 6, border: '1px solid #e5e7eb' }}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="flex flex-col gap-1.5">
                      {allocationData.map((entry) => (
                        <div key={entry.name} className="flex items-center justify-between">
                          <div className="flex items-center gap-1.5 min-w-0">
                            <span className="size-2.5 rounded-full shrink-0" style={{ backgroundColor: entry.color }} />
                            <span className="text-xs text-gray-600 truncate">{entry.name}</span>
                          </div>
                          <span className="text-xs font-semibold text-gray-800 shrink-0">{entry.value}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Top Holdings */}
            <Card className="h-full">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold text-gray-700">
                  Top Holdings
                  {holdings.length > 0 && (
                    <span className="ml-1.5 text-xs font-normal text-gray-400">({holdings.length})</span>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {holdings.length === 0 ? (
                  <p className="text-xs text-gray-400">No holdings data</p>
                ) : (
                  <div className="flex flex-col gap-2.5">
                    {holdings.map((h) => {
                      const weight = Number(h.weight_pct ?? 0)
                      const max = Number(holdings[0]?.weight_pct ?? 1)
                      return (
                        <div key={h.id} className="space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-gray-700 truncate max-w-[75%]">{h.instrument_name}</span>
                            <span className="text-xs font-semibold text-gray-800">{weight.toFixed(2)}%</span>
                          </div>
                          <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full bg-blue-500"
                              style={{ width: `${(weight / max) * 100}%` }}
                            />
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Fund Info */}
            <Card className="h-full">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold text-gray-700">Fund Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <InfoRow label="Manager" value={fund.manager} />
                  <InfoRow label="Benchmark" value={fund.benchmark} />
                  <InfoRow label="Classification" value={fund.asisa_classification} />
                  <InfoRow label="Risk Profile" value={fund.risk_profile} />
                  <InfoRow label="Portfolio Size" value={fund.portfolio_size} />
                  <InfoRow
                    label="Launch Date"
                    value={fund.portfolio_launch_date
                      ? new Date(fund.portfolio_launch_date).toLocaleDateString('en-ZA', { year: 'numeric', month: 'long' })
                      : null}
                  />
                </div>

                {annualReturns && (
                  <div>
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Annual Returns (Historical)</p>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="bg-emerald-50 rounded-lg p-2.5 text-center">
                        <p className="text-base font-bold text-emerald-600">{fmt(annualReturns.highest_pct)}</p>
                        <p className="text-[10px] text-gray-500 mt-0.5">Highest</p>
                      </div>
                      <div className="bg-red-50 rounded-lg p-2.5 text-center">
                        <p className="text-base font-bold text-red-500">{fmt(annualReturns.lowest_pct)}</p>
                        <p className="text-[10px] text-gray-500 mt-0.5">Lowest</p>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Row 2: Performance | Fees */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

            {/* Performance */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold text-gray-700">
                  Performance (Annualised)
                  {performance[0]?.as_of_date && (
                    <span className="ml-1.5 text-xs font-normal text-gray-400">
                      as at {new Date(performance[0].as_of_date).toLocaleDateString('en-ZA', { year: 'numeric', month: 'long' })}
                    </span>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {performance.length === 0 ? (
                  <p className="text-xs text-gray-400">No performance data</p>
                ) : (
                  <div className="border rounded-md overflow-hidden text-xs">
                    <table className="w-full">
                      <thead>
                        <tr className="bg-gray-50 border-b">
                          <th className="text-left px-3 py-2 font-semibold text-gray-600">Period</th>
                          <th className="text-right px-3 py-2 font-semibold text-gray-600">Fund</th>
                          <th className="text-right px-3 py-2 font-semibold text-gray-600">Benchmark</th>
                          <th className="text-right px-3 py-2 font-semibold text-gray-600">vs Benchmark</th>
                        </tr>
                      </thead>
                      <tbody>
                        {performance.map((p) => {
                          const diff = p.tracking_difference_pct
                          const diffPositive = diff != null && Number(diff) >= 0
                          return (
                            <tr key={p.id} className="border-b last:border-0 hover:bg-gray-50">
                              <td className="px-3 py-2 font-medium text-gray-700 capitalize">{p.period}</td>
                              <td className="px-3 py-2 text-right font-semibold text-gray-800 tabular-nums">
                                {fmt(p.fund_return_pct)}
                              </td>
                              <td className="px-3 py-2 text-right text-gray-500 tabular-nums">
                                {fmt(p.benchmark_return_pct)}
                              </td>
                              <td className={`px-3 py-2 text-right font-medium tabular-nums ${
                                diff == null ? 'text-gray-400' : diffPositive ? 'text-emerald-600' : 'text-red-500'
                              }`}>
                                {diff == null ? '—' : `${diffPositive ? '+' : ''}${Number(diff).toFixed(2)}%`}
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Fees */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold text-gray-700">
                  Fees (incl. VAT)
                  {fee?.effective_date && (
                    <span className="ml-1.5 text-xs font-normal text-gray-400">
                      as at {new Date(fee.effective_date).toLocaleDateString('en-ZA', { year: 'numeric', month: 'long' })}
                    </span>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {!fee ? (
                  <p className="text-xs text-gray-400">No fee data available</p>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1.5">Cost Ratios</p>
                      <FeeRow label="Total Expense Ratio (TER)" value={fee.ter} />
                      <FeeRow label="Transaction Cost (TC)" value={fee.transaction_cost_pct} />
                      <FeeRow label="Total Investment Charge (TIC)" value={fee.total_investment_charge_pct} />
                    </div>

                    <div>
                      <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1.5">Annual Fees</p>
                      <FeeRow label="Manager Annual Fee" value={fee.manager_annual_fee_pct} />
                      <FeeRow label="Advice Annual Fee (max.)" value={fee.advice_annual_fee_max_pct} />
                    </div>

                    {(fee.manager_initial_fee_pct != null || fee.advice_initial_fee_max_pct != null) && (
                      <div>
                        <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wide mb-1.5">Initial Fees</p>
                        <FeeRow label="Manager Initial Fee" value={fee.manager_initial_fee_pct} />
                        <FeeRow label="Advice Initial Fee (max.)" value={fee.advice_initial_fee_max_pct} />
                      </div>
                    )}

                    <div className="pt-1 border-t border-gray-100 flex justify-between text-xs">
                      <span className="text-gray-400">Currency</span>
                      <span className="font-medium text-gray-600">{fee.currency}</span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

          </div>
        </div>
      )}
    </div>
  )
}
