import React from "react";
import { Button } from "./button";
import { cn } from "@/lib/utils";

interface ToggleButtonProps {
  isSelected: boolean;
  onClick: () => void;
  children: React.ReactNode;
  className?: string;
  size?: "default" | "sm" | "lg" | "icon";
  variant?: "default" | "accent" | "mystic";
}

export function ToggleButton({
  isSelected,
  onClick,
  children,
  className,
  size = "icon",
  variant = "default",
}: ToggleButtonProps) {
  const getVariantStyles = () => {
    switch (variant) {
      case "accent":
        return {
          selected:
            "bg-accent text-accent-foreground border-2 border-accent shadow-md ring-2 ring-accent/30",
          unselected:
            "bg-background border-0 text-muted-foreground hover:bg-accent/10 hover:text-accent-foreground",
        };
      case "mystic":
        return {
          selected:
            "bg-gradient-to-r from-mystic-500 to-purple-600 text-white border-2 border-mystic-400 shadow-lg ring-2 ring-mystic-300/40",
          unselected:
            "bg-background border-0 text-muted-foreground hover:bg-mystic-50 dark:hover:bg-mystic-900/20 hover:text-mystic-700 dark:hover:text-mystic-300",
        };
      default:
        return {
          selected:
            "bg-primary text-primary-foreground border-2 border-primary shadow-md ring-2 ring-primary/30",
          unselected:
            "bg-background border-0 text-muted-foreground hover:bg-accent hover:text-accent-foreground",
        };
    }
  };

  const styles = getVariantStyles();

  return (
    <Button
      variant="ghost"
      size={size}
      onClick={onClick}
      className={cn(
        "transition-all duration-200",
        isSelected ? styles.selected : styles.unselected,
        className
      )}
    >
      {children}
    </Button>
  );
}

interface ToggleGroupProps {
  value: string;
  onValueChange: (value: string) => void;
  options: Array<{
    value: string;
    label?: string;
    icon?: React.ReactNode;
  }>;
  className?: string;
  variant?: "default" | "accent" | "mystic";
  size?: "default" | "sm" | "lg" | "icon";
}

export function ToggleGroup({
  value,
  onValueChange,
  options,
  className,
  variant = "default",
  size = "icon",
}: ToggleGroupProps) {
  return (
    <div className={cn("flex gap-2", className)}>
      {options.map((option) => (
        <ToggleButton
          key={option.value}
          isSelected={value === option.value}
          onClick={() => onValueChange(option.value)}
          variant={variant}
          size={size}
        >
          {option.icon || option.label}
        </ToggleButton>
      ))}
    </div>
  );
}
