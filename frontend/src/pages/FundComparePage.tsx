import { useEffect, useState } from 'react'
import { GitCompareArrows } from 'lucide-react'
import { FundSelection } from '@/components/FundSelection'
import { FundSimilarityOverlap } from '@/components/FundSimilarityOverlap'
import { OverlappingHoldings } from '@/components/OverlappingHoldings'

interface Fund {
  id: string
  name: string
  manager: string | null
  risk_profile: string | null
}

interface Holding {
  id: string
  instrument_name: string
  weight_pct: number | null
}

interface FundData {
  holdings: Holding[]
  loading: boolean
}

interface FundComparePros {
  funds: Fund[]
  loading: boolean
}

const COLORS = ['#4f46e5', '#0ea5e9', '#f59e0b', '#8b5cf6']
const LABELS = ['Fund A', 'Fund B', 'Fund C', 'Fund D']

export function FundComparePage({ funds, loading }: FundComparePros) {
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [fundData, setFundData] = useState<Record<string, FundData>>({})

  useEffect(() => {
    for (const id of selectedIds) {
      if (fundData[id]) continue
      setFundData(prev => ({ ...prev, [id]: { holdings: [], loading: true } }))
      fetch(`/api/funds/${id}/holdings`)
        .then(r => r.ok ? r.json() : [])
        .then(holdings => {
          setFundData(prev => ({ ...prev, [id]: { holdings, loading: false } }))
        })
    }
  }, [selectedIds])

  const selected = selectedIds
    .map((id, i) => ({ id, fund: funds.find(f => f.id === id)!, data: fundData[id], color: COLORS[i % COLORS.length], label: LABELS[i] }))
    .filter(x => x.fund)

  const allLoaded = selected.length >= 2 && selected.every(x => x.data && !x.data.loading)

  function computeOverlap(holdingsA: Holding[], holdingsB: Holding[]): number {
    const mapB = new Map(holdingsB.map(h => [h.instrument_name, Number(h.weight_pct ?? 0)]))
    return holdingsA.reduce((sum, h) => {
      const wA = Number(h.weight_pct ?? 0)
      const wB = mapB.get(h.instrument_name) ?? 0
      return sum + Math.min(wA, wB)
    }, 0)
  }

  const fundEntries = selected.map(s => ({ label: s.label, name: s.fund.name, color: s.color }))

  const pairs = allLoaded
    ? selected.flatMap((a, i) =>
        selected.slice(i + 1).map(b => ({
          fundA: a.label,
          fundB: b.label,
          overlap: computeOverlap(a.data.holdings, b.data.holdings),
        }))
      )
    : []

  const sharedHoldings = allLoaded
    ? (() => {
        const allNames = new Set(selected.flatMap(s => s.data.holdings.map(h => h.instrument_name)))
        return Array.from(allNames)
          .map(name => {
            const weights = selected.map(s => Number(s.data.holdings.find(h => h.instrument_name === name)?.weight_pct ?? 0))
            const inFunds = weights.filter(w => w > 0).length
            const avgWeight = weights.filter(w => w > 0).reduce((s, w) => s + w, 0) / inFunds
            return { name, inFunds, overlap: avgWeight }
          })
          .filter(x => x.inFunds >= 2)
          .sort((a, b) => b.overlap - a.overlap)
          .slice(0, 10)
      })()
    : []

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-3 px-6 py-3 bg-white border-b border-gray-200">
        <GitCompareArrows className="size-5 text-blue-600 shrink-0" />
        <h1 className="text-base font-bold text-gray-900 shrink-0">Compare Funds</h1>
        <div className="flex-1">
          <FundSelection
            funds={funds}
            selectedIds={selectedIds}
            onChange={setSelectedIds}
            loading={loading}
            placeholder="Select 2–4 funds to compare…"
          />
        </div>
      </div>

      <div className="flex-1 p-6 overflow-auto">
        {selected.length < 2 && (
          <p className="text-sm text-gray-400">Select at least 2 funds to see overlap analysis.</p>
        )}

        {selected.length >= 2 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <FundSimilarityOverlap funds={fundEntries} pairs={pairs} />
            <OverlappingHoldings holdings={sharedHoldings} />
          </div>
        )}
      </div>
    </div>
  )
}
