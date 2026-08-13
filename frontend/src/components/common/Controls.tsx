import type { InputHTMLAttributes, SelectHTMLAttributes, TextareaHTMLAttributes } from "react"
import { cn } from "@/lib/utils"

const base =
  "w-full rounded-md border border-border bg-surface-2/50 text-sm text-foreground placeholder:text-muted transition-colors focus:border-primary/60 focus:outline-none focus:ring-1 focus:ring-primary/40"

export function TextInput({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={cn(base, "h-9 px-3", className)} {...props} />
}

export function TextArea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className={cn(base, "px-3 py-2 leading-relaxed", className)} {...props} />
}

export function Select({ className, children, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select className={cn(base, "h-9 px-2.5 pr-8", className)} {...props}>
      {children}
    </select>
  )
}

export function Field({ label, children, hint }: { label: string; children: React.ReactNode; hint?: string }) {
  return (
    <label className="block">
      <span className="mb-1 block text-[11px] font-medium uppercase tracking-wider text-muted">{label}</span>
      {children}
      {hint && <span className="mt-1 block text-[11px] text-muted">{hint}</span>}
    </label>
  )
}

export function Toggle({ checked, onChange, label }: { checked: boolean; onChange: (v: boolean) => void; label: string }) {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      className={cn(
        "inline-flex items-center gap-2 rounded-md border px-3 h-9 text-xs font-medium transition-colors",
        checked
          ? "border-primary/40 bg-primary/12 text-primary"
          : "border-border bg-surface-2/50 text-muted hover:text-foreground",
      )}
      aria-pressed={checked}
    >
      <span
        className={cn(
          "flex h-4 w-7 items-center rounded-full p-0.5 transition-colors",
          checked ? "bg-primary/80" : "bg-border-strong",
        )}
      >
        <span
          className={cn(
            "h-3 w-3 rounded-full bg-foreground transition-transform",
            checked ? "translate-x-3" : "translate-x-0",
          )}
        />
      </span>
      {label}
    </button>
  )
}
