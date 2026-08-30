"use client";

import { ExternalLink, MoreHorizontal, Pencil, Plus, Tag, Trash2, X } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { getErrorMessage } from "@/lib/errors";
import { attachTag, deleteBookmark, detachTag } from "@/lib/api/bookmarks";
import type { Bookmark, Tag as TagType } from "@/lib/types";
import { cn } from "@/lib/utils";

function hostname(url: string) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}

type Props = {
  bookmark: Bookmark;
  tags: TagType[];
  index: number;
  onEdit: (bookmark: Bookmark) => void;
  onChanged: () => void;
};

export function BookmarkCard({ bookmark, tags, index, onEdit, onChanged }: Props) {
  const [confirmOpen, setConfirmOpen] = useState(false);
  const attached = new Set(bookmark.tags.map((tag) => tag.id));
  const available = tags.filter((tag) => tag.id && !attached.has(tag.id));

  async function onDelete() {
    try {
      await deleteBookmark(bookmark.id);
      toast.success("Bookmark removed");
      onChanged();
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  }

  async function onAttach(tagId: number) {
    try {
      await attachTag(bookmark.id, tagId);
      onChanged();
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  }

  async function onDetach(tagId: number) {
    try {
      await detachTag(bookmark.id, tagId);
      onChanged();
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  }

  return (
    <Card
      className={cn(
        "stagger-in group relative overflow-hidden border-border/70 bg-card/80 transition-all duration-300",
        "hover:-translate-y-1 hover:border-primary/30 hover:shadow-[0_12px_40px_-24px_oklch(0.78_0.14_70_/_0.55)]",
      )}
      style={{ animationDelay: `${Math.min(index, 10) * 45}ms` }}
    >
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-primary/40 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
      <CardHeader className="flex-row items-start justify-between gap-3 space-y-0 pb-2">
        <div className="min-w-0">
          <CardTitle className="truncate text-base">{bookmark.title}</CardTitle>
          <a
            href={bookmark.url}
            target="_blank"
            rel="noreferrer"
            className="mt-1 inline-flex max-w-full items-center gap-1 truncate text-xs text-muted-foreground transition-colors hover:text-primary"
          >
            {hostname(bookmark.url)}
            <ExternalLink className="size-3 shrink-0" />
          </a>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon-sm" className="shrink-0">
              <MoreHorizontal className="size-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onClick={() => onEdit(bookmark)}>
              <Pencil className="size-4" />
              Edit
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem variant="destructive" onClick={() => setConfirmOpen(true)}>
              <Trash2 className="size-4" />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
        <AlertDialog open={confirmOpen} onOpenChange={setConfirmOpen}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete this bookmark?</AlertDialogTitle>
              <AlertDialogDescription>
                {bookmark.title} will be removed from your stash.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={onDelete}>Delete</AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </CardHeader>
      <CardContent className="space-y-3">
        {bookmark.notes ? (
          <p className="line-clamp-2 text-sm text-muted-foreground">{bookmark.notes}</p>
        ) : null}
        <div className="flex flex-wrap items-center gap-1.5">
          {bookmark.tags.map((tag) => (
            <Badge
              key={tag.id}
              variant="secondary"
              className="gap-1 pr-1 transition-transform duration-150 hover:scale-105"
            >
              {tag.name}
              <button
                type="button"
                className="rounded-full p-0.5 hover:bg-foreground/10"
                onClick={() => tag.id && onDetach(tag.id)}
                aria-label={`Remove ${tag.name}`}
              >
                <X className="size-3" />
              </button>
            </Badge>
          ))}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="xs" className="h-6 px-1.5 text-muted-foreground">
                <Plus className="size-3" />
                Tag
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start">
              {available.length === 0 ? (
                <DropdownMenuItem disabled>
                  <Tag className="size-4" />
                  No more tags
                </DropdownMenuItem>
              ) : (
                available.map((tag) => (
                  <DropdownMenuItem key={tag.id} onClick={() => tag.id && onAttach(tag.id)}>
                    {tag.name}
                  </DropdownMenuItem>
                ))
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardContent>
    </Card>
  );
}
