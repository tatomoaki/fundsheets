import { useState } from 'react'
import { Download, FileOutput } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

type Tab = 'exposure' | 'holding'

const STATS = {
  topHolding: { name: 'Naspers Ltd', weight: 18.3 },
  totalEquity: 63.3,
  geographic: { local: 16.3, global: 3.0 },
}

export function ExposureSummary() {
  const [tab, setTab] = useState<Tab>('exposure')

  return (
    <div className="sticky bottom-0 z-40 bg-white border-t border-gray-200 shadow-[0_-2px_8px_rgba(0,0,0,0.06)]">
      <div className="flex items-center justify-between px-6 py-2 gap-4 flex-wrap">
        {/* Tabs */}
        <div className="flex items-stretch gap-0 shrink-0 border rounded-md overflow-hidden text-xs font-medium">
          <button
            onClick={() => setTab('exposure')}
            className={cn(
              'px-3 py-1.5 transition-colors',
              tab === 'exposure' ? 'bg-[#1a2e4a] text-white' : 'text-gray-600 hover:bg-gray-50'
            )}
          >
            Exposure Summary
          </button>
          <button
            onClick={() => setTab('holding')}
            className={cn(
              'px-3 py-1.5 border-l transition-colors',
              tab === 'holding' ? 'bg-[#1a2e4a] text-white' : 'text-gray-600 hover:bg-gray-50'
            )}
          >
            Top Single Holding: {STATS.topHolding.name} {STATS.topHolding.weight}%
          </button>
        </div>

        {/* Stats */}
        <div className="flex items-center gap-5 flex-wrap text-xs text-gray-600">
          <div className="flex items-center gap-1.5">
            <span className="font-medium text-gray-500">Total Equity Exposure:</span>
            <span className="font-bold text-gray-900">{STATS.totalEquity}%</span>
          </div>
          <div className="h-3 w-px bg-gray-300" />
          <div className="flex items-center gap-1.5">
            <span className="font-medium text-gray-500">Geographic Allocation:</span>
            <span className="font-bold text-gray-900">{STATS.geographic.local}% Local</span>
            <span className="text-gray-400">|</span>
            <span className="font-bold text-gray-900">{STATS.geographic.global}% Global</span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 shrink-0">
          <Button variant="outline" size="sm" className="text-xs gap-1.5">
            <FileOutput className="size-3.5" />
            Export PDF
          </Button>
          <Button size="sm" className="text-xs gap-1.5 bg-[#2563eb] hover:bg-[#1d4ed8] text-white border-0">
            <Download className="size-3.5" />
            Download Fund Sheet
          </Button>
        </div>
      </div>
    </div>
  )
}
