import { BarChart2, ChevronRight, GitCompareArrows, TrendingUp, Users } from 'lucide-react'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from '@/components/ui/sidebar'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'

export type NavPage = 'Funds' | 'FundCompare' | 'Clients'

interface AppSidebarProps {
  activePage: NavPage
  onNavChange: (page: NavPage) => void
}

export function AppSidebar({ activePage, onNavChange }: AppSidebarProps) {
  const fundsOpen = activePage === 'Funds' || activePage === 'FundCompare'

  return (
    <Sidebar>
      <SidebarHeader className="border-b border-sidebar-border px-4 py-3">
        <div className="flex items-center gap-2.5">
          <BarChart2 className="size-5 text-primary shrink-0" />
          <span className="text-[14px] font-bold tracking-tight leading-tight">
            Fund Portfolio Intelligence
          </span>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              <Collapsible defaultOpen={fundsOpen} className="group/collapsible">
                <SidebarMenuItem>
                  <CollapsibleTrigger>
                    <SidebarMenuButton
                      isActive={activePage === 'Funds'}
                      onClick={() => onNavChange('Funds')}
                      tooltip="Funds"
                    >
                      <TrendingUp />
                      <span>Funds</span>
                    </SidebarMenuButton>
                  </CollapsibleTrigger>

                  
                </SidebarMenuItem>
              </Collapsible>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-sidebar-border px-4 py-3">
        <div className="flex items-center gap-2.5">
          <Avatar className="size-8 shrink-0">
            <AvatarFallback className="bg-primary text-primary-foreground text-[11px] font-bold">JS</AvatarFallback>
          </Avatar>
          <div className="flex flex-col min-w-0">
            <span className="text-[13px] font-medium truncate">John Smith</span>
            <span className="text-[11px] text-muted-foreground truncate">Financial Advisor</span>
          </div>
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}
