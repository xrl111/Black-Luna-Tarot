import React from "react";
import { cn } from "@/lib/utils";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./select";

// Enhanced Select with glass effect for Tarot theme
interface TarotSelectProps {
  value?: string;
  onValueChange?: (value: string) => void;
  placeholder?: string;
  children: React.ReactNode;
  className?: string;
  variant?: "default" | "glass" | "mystical";
}

export function TarotSelect({
  value,
  onValueChange,
  placeholder,
  children,
  className,
  variant = "default",
}: TarotSelectProps) {
  const getVariantClasses = () => {
    switch (variant) {
      case "glass":
        return {
          trigger:
            "select-glass border-mystic-200/30 dark:border-mystic-700/30",
          content: "select-glass shadow-2xl",
          item: "hover:bg-mystic-100/80 dark:hover:bg-mystic-800/40",
        };
      case "mystical":
        return {
          trigger:
            "bg-gradient-to-br from-mystic-50/80 to-purple-50/80 dark:from-mystic-900/40 dark:to-purple-900/40 border-mystic-300/50 dark:border-mystic-600/50 backdrop-blur-sm",
          content:
            "bg-gradient-to-br from-white/95 to-mystic-50/95 dark:from-slate-900/95 dark:to-mystic-900/95 backdrop-blur-lg border-mystic-200/50 dark:border-mystic-700/50",
          item: "hover:bg-mystic-100/60 dark:hover:bg-mystic-800/30 data-[highlighted]:bg-mystic-200/80 dark:data-[highlighted]:bg-mystic-700/50",
        };
      default:
        return {
          trigger: "tarot-select-trigger",
          content: "tarot-select-content",
          item: "tarot-select-item",
        };
    }
  };

  const variantClasses = getVariantClasses();

  return (
    <Select value={value} onValueChange={onValueChange}>
      <SelectTrigger className={cn(variantClasses.trigger, className)}>
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent className={variantClasses.content}>
        {React.Children.map(children, (child) => {
          if (React.isValidElement(child) && child.type === SelectItem) {
            return React.cloneElement(child as React.ReactElement<any>, {
              className: cn(
                variantClasses.item,
                (child.props as any)?.className
              ),
            });
          }
          return child;
        })}
      </SelectContent>
    </Select>
  );
}

// Pre-styled SelectItem for convenience
interface TarotSelectItemProps {
  value: string;
  children: React.ReactNode;
  className?: string;
}

export function TarotSelectItem({
  value,
  children,
  className,
}: TarotSelectItemProps) {
  return (
    <SelectItem value={value} className={cn("tarot-select-item", className)}>
      {children}
    </SelectItem>
  );
}
