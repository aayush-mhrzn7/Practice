"use client";

import { Search, X } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import type { Tag } from "@/lib/types";
import { cn } from "@/lib/utils";

type Props = {
  query: string;
  onQueryChange: (value: string) => void;
  tags: Tag[];
  activeTag: string | null;
  onTagChange: (name: string | null) => void;
};

export function BookmarkFilters({
  query,
  onQueryChange,
  tags,
  activeTag,
  onTagChange,
}: Props) {
  return (
    <div className="space-y-3">
      <div className="relative">
        <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          placeholder="Search title or URL"
          className="h-10 bg-card/60 pl-9 pr-9 transition-shadow duration-200 focus-visible:shadow-[0_0_0_4px_oklch(0.78_0.14_70_/_0.12)]"
        />
        {query ? (
          <Button
            type="button"
            variant="ghost"
            size="icon-xs"
            className="absolute top-1/2 right-2 -translate-y-1/2"
            onClick={() => onQueryChange("")}
            aria-label="Clear search"
          >
            <X className="size-3.5" />
          </Button>
        ) : null}
      </div>
      <div className="flex flex-wrap gap-1.5">
        <Badge
          asChild
          variant={activeTag ? "outline" : "default"}
          className="cursor-pointer transition-transform duration-150 hover:scale-105"
        >
          <button type="button" onClick={() => onTagChange(null)}>
            All
          </button>
        </Badge>
        {tags.map((tag) => {
          const selected = activeTag === tag.name;
          return (
            <Badge
              key={tag.id}
              asChild
              variant={selected ? "default" : "outline"}
              className={cn(
                "cursor-pointer transition-transform duration-150 hover:scale-105",
                selected && "shadow-sm",
              )}
            >
              <button type="button" onClick={() => onTagChange(selected ? null : tag.name)}>
                {tag.name}
              </button>
            </Badge>
          );
        })}
      </div>
    </div>
  );
}
