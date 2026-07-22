import { useState } from 'react'
import { Check, ChevronsUpDown, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '@/components/ui/command'
import { cn } from '@/lib/utils'

interface Fund {
  id: string
  name: string
}

interface FundSelectionProps {
  funds: Fund[]
  selectedIds: string[]
  onChange: (ids: string[]) => void
  loading?: boolean
  placeholder?: string
}

export function FundSelection({ funds, selectedIds, onChange, loading = false, placeholder }: FundSelectionProps) {
  const [open, setOpen] = useState(false)

  function toggle(id: string) {
    onChange(selectedIds.includes(id) ? selectedIds.filter((x) => x !== id) : [...selectedIds, id])
  }

  const selectedFunds = funds.filter((f) => selectedIds.includes(f.id))

  return (
    <div className="flex items-center gap-3 flex-wrap w-full">
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            role="combobox"
            aria-expanded={open}
            disabled={loading}
            className="min-w-[280px] max-w-[560px] flex-1 justify-between h-auto min-h-[38px] px-3 py-1.5 font-normal"
          >
            {selectedFunds.length === 0 ? (
              <span className="text-muted-foreground text-sm">
                {loading ? 'Loading funds…' : (placeholder ?? 'Select funds…')}
              </span>
            ) : (
              <div className="flex flex-wrap gap-1">
                {selectedFunds.map((f) => (
                  <Badge
                    key={f.id}
                    variant="secondary"
                    className="bg-blue-100 text-blue-700 hover:bg-blue-100 gap-1 pr-1 rounded"
                  >
                    {f.name}
                    <span
                      role="button"
                      aria-label={`Remove ${f.name}`}
                      className="rounded-sm hover:bg-blue-200 p-0.5 cursor-pointer"
                      onClick={(e) => { e.stopPropagation(); toggle(f.id) }}
                    >
                      <X className="size-3" />
                    </span>
                  </Badge>
                ))}
              </div>
            )}
            <div className="flex items-center gap-1 ml-2 shrink-0">
              {selectedFunds.length > 0 && (
                <span
                  role="button"
                  aria-label="Clear all"
                  className="rounded-full hover:bg-gray-100 p-0.5 cursor-pointer"
                  onClick={(e) => { e.stopPropagation(); onChange([]) }}
                >
                  <X className="size-3.5 text-gray-400" />
                </span>
              )}
              <ChevronsUpDown className="size-4 text-gray-400 shrink-0" />
            </div>
          </Button>
        </PopoverTrigger>
        <PopoverContent className="p-0 w-[var(--radix-popover-trigger-width)]" align="start">
          <Command>
            <CommandInput placeholder="Search funds..." />
            <CommandList>
              <CommandEmpty>No funds found.</CommandEmpty>
              <CommandGroup>
                {funds.map((fund) => (
                  <CommandItem
                    key={fund.id}
                    value={fund.name}
                    onSelect={() => toggle(fund.id)}
                  >
                    <Check className={cn('size-4', selectedIds.includes(fund.id) ? 'opacity-100' : 'opacity-0')} />
                    {fund.name}
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </PopoverContent>
      </Popover>

      {selectedFunds.length > 0 && (
        <span className="text-xs text-blue-600 font-medium whitespace-nowrap">
          {selectedFunds.length} fund{selectedFunds.length !== 1 ? 's' : ''} selected
        </span>
      )}
    </div>
  )
}
