import { BarChart2, TrendingUp, Users } from 'lucide-react'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { cn } from '@/lib/utils'

export type NavPage = 'Funds' | 'Clients'

const NAV_ITEMS: { label: NavPage; icon: React.ElementType }[] = [
  { label: 'Funds',   icon: TrendingUp },
  { label: 'Clients', icon: Users },
]

interface HeaderProps {
  activePage: NavPage
  onNavChange: (page: NavPage) => void
}

export function Header({ activePage, onNavChange }: HeaderProps) {
  return (
    <header className="flex h-14 items-center justify-between bg-[#1a2e4a] px-6 sticky top-0 z-50 shadow-md">
      <div className="flex items-center gap-2.5 shrink-0">
        <BarChart2 className="size-5 text-[#4a9eff]" />
        <span className="text-[15px] font-bold text-white tracking-tight">Fund Portfolio Intelligence</span>
      </div>

      <nav className="flex items-stretch h-full">
        {NAV_ITEMS.map(({ label, icon: Icon }) => (
          <button
            key={label}
            onClick={() => onNavChange(label)}
            className={cn(
              'flex items-center gap-2 px-5 h-full text-[13px] font-medium border-b-[3px] transition-colors cursor-pointer',
              activePage === label
                ? 'text-white border-[#4a9eff]'
                : 'text-white/60 border-transparent hover:text-white/90 hover:border-white/30'
            )}
          >
            <Icon className="size-3.5" />
            {label}
          </button>
        ))}
      </nav>

      <div className="flex items-center gap-2.5 shrink-0">
        <Avatar className="size-8">
          <AvatarFallback className="bg-[#4a9eff] text-white text-[11px] font-bold">JS</AvatarFallback>
        </Avatar>
        <span className="text-[13px] text-white/90 font-medium whitespace-nowrap">
          John Smith <span className="text-white/50 font-normal">| Financial Advisor</span>
        </span>
      </div>
    </header>
  )
}
