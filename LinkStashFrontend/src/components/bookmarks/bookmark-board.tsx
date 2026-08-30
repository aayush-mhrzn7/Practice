"use client";

import { Plus } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";

import { BookmarkCard } from "@/components/bookmarks/bookmark-card";
import { BookmarkDialog } from "@/components/bookmarks/bookmark-dialog";
import { BookmarkFilters } from "@/components/bookmarks/bookmark-filters";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useDebouncedValue } from "@/hooks/use-debounced-value";
import { listBookmarks } from "@/lib/api/bookmarks";
import { listTags } from "@/lib/api/tags";
import { getErrorMessage } from "@/lib/errors";
import type { Bookmark, Paginated, Tag } from "@/lib/types";

const PAGE_SIZE = 12;

export function BookmarkBoard() {
  const [query, setQuery] = useState("");
  const [tag, setTag] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [tags, setTags] = useState<Tag[]>([]);
  const [result, setResult] = useState<Paginated<Bookmark> | null>(null);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editing, setEditing] = useState<Bookmark | null>(null);
  const debouncedQuery = useDebouncedValue(query);

  const loadTags = useCallback(async () => {
    const data = await listTags();
    setTags(data.data);
  }, []);

  const loadBookmarks = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listBookmarks({
        page,
        page_size: PAGE_SIZE,
        q: debouncedQuery || undefined,
        tag: tag || undefined,
      });
      setResult(data);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }, [page, debouncedQuery, tag]);

  useEffect(() => {
    void loadTags();
  }, [loadTags]);

  useEffect(() => {
    setPage(1);
  }, [debouncedQuery, tag]);

  useEffect(() => {
    void loadBookmarks();
  }, [loadBookmarks]);

  const totalPages = result ? Math.max(1, Math.ceil(result.total / result.page_size)) : 1;

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-1">
          <p className="text-xs font-medium tracking-[0.18em] text-primary/80 uppercase">Library</p>
          <h1 className="text-2xl font-semibold tracking-tight">Bookmarks</h1>
          <p className="text-sm text-muted-foreground">
            {result ? `${result.total} saved` : "Loading your stash"}
          </p>
        </div>
        <Button
          onClick={() => {
            setEditing(null);
            setDialogOpen(true);
          }}
          className="self-start transition-transform duration-200 hover:scale-[1.02]"
        >
          <Plus className="size-4" />
          New bookmark
        </Button>
      </div>

      <BookmarkFilters
        query={query}
        onQueryChange={setQuery}
        tags={tags}
        activeTag={tag}
        onTagChange={setTag}
      />

      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <Skeleton key={index} className="h-40 rounded-xl" />
          ))}
        </div>
      ) : result?.data.length ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {result.data.map((bookmark, index) => (
            <BookmarkCard
              key={bookmark.id}
              bookmark={bookmark}
              tags={tags}
              index={index}
              onEdit={(item) => {
                setEditing(item);
                setDialogOpen(true);
              }}
              onChanged={() => {
                void loadBookmarks();
                void loadTags();
              }}
            />
          ))}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-border/80 bg-card/40 px-6 py-16 text-center">
          <p className="text-sm font-medium">Nothing in this corner yet</p>
          <p className="mt-1 max-w-sm text-sm text-muted-foreground">
            Save a link, or clear search and tags to see the rest of your stash.
          </p>
        </div>
      )}

      {result && result.total > PAGE_SIZE ? (
        <div className="flex items-center justify-center gap-3">
          <Button
            variant="outline"
            disabled={page <= 1}
            onClick={() => setPage((current) => Math.max(1, current - 1))}
          >
            Previous
          </Button>
          <span className="text-xs text-muted-foreground">
            {page} / {totalPages}
          </span>
          <Button
            variant="outline"
            disabled={page >= totalPages}
            onClick={() => setPage((current) => current + 1)}
          >
            Next
          </Button>
        </div>
      ) : null}

      <BookmarkDialog
        open={dialogOpen}
        bookmark={editing}
        onOpenChange={setDialogOpen}
        onSaved={() => void loadBookmarks()}
      />
    </div>
  );
}
