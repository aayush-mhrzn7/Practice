"use client";

import { Pencil, Plus, Trash2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
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
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { createTag, deleteTag, listTags, updateTag } from "@/lib/api/tags";
import { getErrorMessage } from "@/lib/errors";
import type { Tag } from "@/lib/types";

export function TagManager() {
  const [tags, setTags] = useState<Tag[]>([]);
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [draft, setDraft] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listTags();
      setTags(data.data);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function onCreate(event: React.FormEvent) {
    event.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) return;
    try {
      await createTag(trimmed);
      setName("");
      toast.success("Tag created");
      await load();
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  }

  async function onRename(id: number) {
    const trimmed = draft.trim();
    if (!trimmed) return;
    try {
      await updateTag(id, trimmed);
      setEditingId(null);
      toast.success("Tag renamed");
      await load();
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  }

  async function onDelete(id: number) {
    try {
      await deleteTag(id);
      toast.success("Tag removed");
      await load();
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  }

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6">
      <div className="space-y-1">
        <p className="text-xs font-medium tracking-[0.18em] text-primary/80 uppercase">Organize</p>
        <h1 className="text-2xl font-semibold tracking-tight">Tags</h1>
        <p className="text-sm text-muted-foreground">Names are stored lowercase. Attach them from a bookmark card.</p>
      </div>

      <form onSubmit={onCreate} className="flex gap-2">
        <Input
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="python, docs, later…"
          className="h-10 bg-card/60"
        />
        <Button type="submit" className="transition-transform duration-200 hover:scale-[1.02]">
          <Plus className="size-4" />
          Add
        </Button>
      </form>

      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, index) => (
            <Skeleton key={index} className="h-14 rounded-xl" />
          ))}
        </div>
      ) : tags.length === 0 ? (
        <div className="rounded-2xl border border-dashed px-6 py-12 text-center text-sm text-muted-foreground">
          No tags yet. Add one to start grouping links.
        </div>
      ) : (
        <div className="space-y-2">
          {tags.map((tag, index) => (
            <Card
              key={tag.id}
              className="stagger-in border-border/70 bg-card/80 transition-all duration-200 hover:border-primary/25"
              style={{ animationDelay: `${Math.min(index, 12) * 40}ms` }}
            >
              <CardContent className="flex items-center justify-between gap-3 py-3">
                {editingId === tag.id ? (
                  <form
                    className="flex min-w-0 flex-1 gap-2"
                    onSubmit={(event) => {
                      event.preventDefault();
                      if (tag.id) void onRename(tag.id);
                    }}
                  >
                    <Input
                      value={draft}
                      onChange={(event) => setDraft(event.target.value)}
                      autoFocus
                      className="h-8"
                    />
                    <Button type="submit" size="sm">
                      Save
                    </Button>
                    <Button type="button" size="sm" variant="ghost" onClick={() => setEditingId(null)}>
                      Cancel
                    </Button>
                  </form>
                ) : (
                  <p className="truncate font-medium">{tag.name}</p>
                )}
                {editingId === tag.id ? null : (
                  <div className="flex shrink-0 gap-1">
                    <Button
                      variant="ghost"
                      size="icon-sm"
                      onClick={() => {
                        setEditingId(tag.id ?? null);
                        setDraft(tag.name);
                      }}
                      aria-label={`Rename ${tag.name}`}
                    >
                      <Pencil className="size-4" />
                    </Button>
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button variant="ghost" size="icon-sm" aria-label={`Delete ${tag.name}`}>
                          <Trash2 className="size-4" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Delete {tag.name}?</AlertDialogTitle>
                          <AlertDialogDescription>
                            It will unlink from your library. Bookmarks stay put.
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          <AlertDialogAction onClick={() => tag.id && onDelete(tag.id)}>
                            Delete
                          </AlertDialogAction>
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
