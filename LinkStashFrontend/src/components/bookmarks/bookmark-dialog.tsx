"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { createBookmark, updateBookmark } from "@/lib/api/bookmarks";
import { getErrorMessage } from "@/lib/errors";
import type { Bookmark } from "@/lib/types";

type Props = {
  open: boolean;
  bookmark: Bookmark | null;
  onOpenChange: (open: boolean) => void;
  onSaved: () => void;
};

const empty = { url: "", title: "", notes: "" };

export function BookmarkDialog({ open, bookmark, onOpenChange, onSaved }: Props) {
  const [form, setForm] = useState(empty);
  const [saving, setSaving] = useState(false);
  const editing = Boolean(bookmark);

  useEffect(() => {
    if (bookmark) {
      setForm({
        url: bookmark.url,
        title: bookmark.title,
        notes: bookmark.notes ?? "",
      });
      return;
    }
    setForm(empty);
  }, [bookmark, open]);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSaving(true);
    try {
      if (bookmark) {
        await updateBookmark(bookmark.id, {
          url: form.url,
          title: form.title,
          notes: form.notes || null,
        });
        toast.success("Bookmark updated");
      } else {
        await createBookmark({
          url: form.url,
          title: form.title,
          notes: form.notes || null,
        });
        toast.success("Bookmark saved");
      }
      onSaved();
      onOpenChange(false);
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setSaving(false);
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={onSubmit} className="grid gap-4">
          <DialogHeader>
            <DialogTitle>{editing ? "Edit bookmark" : "Save a link"}</DialogTitle>
            <DialogDescription>
              {editing
                ? "Update the title, URL, or notes. Tags stay on the card."
                : "Drop a URL in. You can tag it after it lands."}
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-2">
            <Label htmlFor="url">URL</Label>
            <Input
              id="url"
              required
              placeholder="https://"
              value={form.url}
              onChange={(event) => setForm((current) => ({ ...current, url: event.target.value }))}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="title">Title</Label>
            <Input
              id="title"
              required
              value={form.title}
              onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="notes">Notes</Label>
            <Textarea
              id="notes"
              rows={3}
              placeholder="Optional context"
              value={form.notes}
              onChange={(event) => setForm((current) => ({ ...current, notes: event.target.value }))}
            />
          </div>
          <DialogFooter>
            <Button type="button" variant="ghost" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" disabled={saving}>
              {saving ? "Saving…" : editing ? "Save changes" : "Add bookmark"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
