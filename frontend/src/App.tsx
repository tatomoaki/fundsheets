import { useEffect, useState } from 'react'
import { AppSidebar } from './components/AppSidebar'
import type { NavPage } from './components/AppSidebar'
import { ChatPanel } from './components/ChatPanel'
import { FundsListPage } from './pages/FundsListPage'
import { FundSheetPage } from './pages/FundSheetPage'
import { FundComparePage } from './pages/FundComparePage'
import { ClientsListPage } from './pages/ClientsListPage'
import { SidebarInset, SidebarProvider, SidebarTrigger } from './components/ui/sidebar'
import './App.css'

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

type View =
  | { page: 'funds-list' }
  | { page: 'fund-detail'; fund: Fund }
  | { page: 'fund-compare' }
  | { page: 'clients' }

function App() {
  const [funds, setFunds] = useState<Fund[]>([])
  const [loading, setLoading] = useState(true)
  const [view, setView] = useState<View>({ page: 'funds-list' })

  useEffect(() => {
    fetch('/api/funds/')
      .then(r => r.ok ? r.json() : [])
      .then(setFunds)
      .finally(() => setLoading(false))
  }, [])

  const activePage: NavPage =
    view.page === 'clients' ? 'Clients' :
    view.page === 'fund-compare' ? 'FundCompare' :
    'Funds'

  function handleNavChange(page: NavPage) {
    if (page === 'Clients') setView({ page: 'clients' })
    else if (page === 'FundCompare') setView({ page: 'fund-compare' })
    else setView({ page: 'funds-list' })
  }

  return (
    <SidebarProvider className="h-svh overflow-hidden">
      <AppSidebar activePage={activePage} onNavChange={handleNavChange} />

      <SidebarInset className="overflow-hidden">
        <div className="flex h-full overflow-hidden">
          <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
            <header className="flex h-10 items-center gap-2 border-b px-4 shrink-0 bg-background">
              <SidebarTrigger />
            </header>

            <div className="flex-1 overflow-y-auto bg-gray-100">
              {view.page === 'funds-list' && (
                <FundsListPage
                  funds={funds}
                  loading={loading}
                  onSelectFund={(fund) => setView({ page: 'fund-detail', fund })}
                />
              )}
              {view.page === 'fund-detail' && (
                <FundSheetPage
                  fund={view.fund}
                  onBack={() => setView({ page: 'funds-list' })}
                />
              )}
              {view.page === 'fund-compare' && (
                <FundComparePage funds={funds} loading={loading} />
              )}
              {view.page === 'clients' && (
                <ClientsListPage />
              )}
            </div>
          </div>

          <ChatPanel />
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}

export default App
