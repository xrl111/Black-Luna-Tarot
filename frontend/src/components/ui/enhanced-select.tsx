import { cn } from "@/lib/utils";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./select";

// Default enhanced select with improved transparency
interface EnhancedSelectProps {
  value?: string;
  onValueChange?: (value: string) => void;
  placeholder?: string;
  options: Array<{
    value: string;
    label: string;
    disabled?: boolean;
  }>;
  className?: string;
  triggerClassName?: string;
  contentClassName?: string;
  itemClassName?: string;
  size?: "sm" | "default";
  variant?: "default" | "enhanced" | "glass" | "mystical";
}

export function EnhancedSelect({
  value,
  onValueChange,
  placeholder,
  options,
  className,
  triggerClassName,
  contentClassName,
  itemClassName,
  size = "default",
  variant = "enhanced",
}: EnhancedSelectProps) {
  const getVariantClasses = () => {
    switch (variant) {
      case "enhanced":
        return {
          trigger: "tarot-select-trigger w-full min-w-[200px]",
          content:
            "tarot-select-content min-w-[var(--radix-select-trigger-width)]",
          item: "tarot-select-item",
        };
      case "glass":
        return {
          trigger:
            "select-glass border-mystic-200/30 dark:border-mystic-700/30 w-full min-w-[200px] focus:ring-2 focus:ring-mystic-300/50",
          content:
            "select-glass shadow-2xl min-w-[var(--radix-select-trigger-width)]",
          item: "hover:bg-mystic-100/80 dark:hover:bg-mystic-800/40 focus:bg-mystic-100/90 dark:focus:bg-mystic-800/50 data-[highlighted]:bg-mystic-100/90 dark:data-[highlighted]:bg-mystic-800/50",
        };
      case "mystical":
        return {
          trigger:
            "bg-gradient-to-br from-mystic-50/80 to-purple-50/80 dark:from-mystic-900/40 dark:to-purple-900/40 border-mystic-300/50 dark:border-mystic-600/50 backdrop-blur-sm w-full min-w-[200px] focus:ring-2 focus:ring-purple-300/50 focus:border-purple-400",
          content:
            "bg-gradient-to-br from-white/95 to-mystic-50/95 dark:from-slate-900/95 dark:to-mystic-900/95 backdrop-blur-lg border-mystic-200/50 dark:border-mystic-700/50 min-w-[var(--radix-select-trigger-width)]",
          item: "hover:bg-mystic-100/60 dark:hover:bg-mystic-800/30 focus:bg-mystic-100/80 dark:focus:bg-mystic-800/40 data-[highlighted]:bg-mystic-200/80 dark:data-[highlighted]:bg-mystic-700/50 data-[state=checked]:bg-purple-100 dark:data-[state=checked]:bg-purple-900/30",
        };
      default:
        return {
          trigger: "w-full min-w-[200px]",
          content: "min-w-[var(--radix-select-trigger-width)]",
          item: "",
        };
    }
  };

  const variantClasses = getVariantClasses();

  return (
    <Select value={value} onValueChange={onValueChange}>
      <SelectTrigger
        className={cn(variantClasses.trigger, triggerClassName, className)}
        size={size}
      >
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent className={cn(variantClasses.content, contentClassName)}>
        {options.map((option) => (
          <SelectItem
            key={option.value}
            value={option.value}
            className={cn(variantClasses.item, itemClassName)}
            disabled={option.disabled}
          >
            {option.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

// Quick presets for common use cases
export function TarotCardSelect(props: Omit<EnhancedSelectProps, "variant">) {
  return <EnhancedSelect {...props} variant="enhanced" />;
}

export function GlassSelect(props: Omit<EnhancedSelectProps, "variant">) {
  return <EnhancedSelect {...props} variant="glass" />;
}

export function MysticalSelect(props: Omit<EnhancedSelectProps, "variant">) {
  return <EnhancedSelect {...props} variant="mystical" />;
}

// Utility function to create consistent option arrays
export function createSelectOptions(
  items: Array<{ value: string; label: string } | string>,
  includeAll = true
): Array<{ value: string; label: string }> {
  const options = items.map((item) =>
    typeof item === "string" ? { value: item, label: item } : item
  );

  if (includeAll) {
    return [{ value: "all", label: "Tất cả" }, ...options];
  }

  return options;
}
