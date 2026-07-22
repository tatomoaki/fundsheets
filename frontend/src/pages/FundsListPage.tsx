import { ChevronRight, TrendingUp } from 'lucide-react'

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

interface FundsListPageProps {
  funds: Fund[]
  loading: boolean
  onSelectFund: (fund: Fund) => void
}

const RISK_COLORS: Record<string, string> = {
  Aggressive:    'bg-red-100 text-red-700',
  Moderate:      'bg-yellow-100 text-yellow-700',
  Conservative:  'bg-green-100 text-green-700',
}

function riskBadgeClass(profile: string | null) {
  if (!profile) return 'bg-gray-100 text-gray-500'
  return RISK_COLORS[profile] ?? 'bg-blue-100 text-blue-700'
}

export function FundsListPage({ funds, loading, onSelectFund }: FundsListPageProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-sm text-gray-400">
        Loading funds…
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="flex items-center gap-2 mb-6">
        <TrendingUp className="size-5 text-blue-600" />
        <h1 className="text-lg font-bold text-gray-900">Funds</h1>
        <span className="ml-1 text-sm text-gray-400">({funds.length})</span>
      </div>

      {funds.length === 0 ? (
        <p className="text-sm text-gray-400">No funds available.</p>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100 bg-gray-50">
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Fund</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Manager</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Risk Profile</th>
                <th className="px-5 py-3" />
              </tr>
            </thead>
            <tbody>
              {funds.map((fund, i) => (
                <tr
                  key={fund.id}
                  onClick={() => onSelectFund(fund)}
                  className={`cursor-pointer hover:bg-blue-50 transition-colors ${i !== funds.length - 1 ? 'border-b border-gray-100' : ''}`}
                >
                  <td className="px-5 py-3.5 font-medium text-gray-900">{fund.name}</td>
                  <td className="px-5 py-3.5 text-gray-500">{fund.manager ?? '—'}</td>
                  <td className="px-5 py-3.5">
                    {fund.risk_profile ? (
                      <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${riskBadgeClass(fund.risk_profile)}`}>
                        {fund.risk_profile}
                      </span>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <ChevronRight className="size-4 text-gray-400 inline" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
