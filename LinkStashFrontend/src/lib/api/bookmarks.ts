import { http } from "@/lib/api/client";
import type { Bookmark, BookmarkDraft, Paginated } from "@/lib/types";

export async function listBookmarks(params: {
  page?: number;
  page_size?: number;
  q?: string;
  tag?: string;
}) {
  const { data } = await http.get<Paginated<Bookmark>>("/bookmarks/", { params });
  return data;
}

export async function createBookmark(payload: BookmarkDraft) {
  const { data } = await http.post<Bookmark>("/bookmarks/", payload);
  return data;
}

export async function updateBookmark(id: number, payload: Partial<BookmarkDraft>) {
  const { data } = await http.patch<Bookmark>(`/bookmarks/${id}`, payload);
  return data;
}

export async function deleteBookmark(id: number) {
  await http.delete(`/bookmarks/${id}`);
}

export async function attachTag(bookmarkId: number, tagId: number) {
  const { data } = await http.post<Bookmark>(`/bookmarks/${bookmarkId}/tags`, {
    tag_id: tagId,
  });
  return data;
}

export async function detachTag(bookmarkId: number, tagId: number) {
  await http.delete(`/bookmarks/${bookmarkId}/tags/${tagId}`);
}
