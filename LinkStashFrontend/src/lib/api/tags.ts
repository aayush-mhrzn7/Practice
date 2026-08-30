import { http } from "@/lib/api/client";
import type { Paginated, Tag } from "@/lib/types";

export async function listTags(params: { page?: number; page_size?: number } = {}) {
  const { data } = await http.get<Paginated<Tag>>("/tags/", {
    params: { page_size: 100, ...params },
  });
  return data;
}

export async function createTag(name: string) {
  const { data } = await http.post<Tag>("/tags/", { name });
  return data;
}

export async function updateTag(id: number, name: string) {
  const { data } = await http.put<Tag>(`/tags/${id}`, { name });
  return data;
}

export async function deleteTag(id: number) {
  await http.delete(`/tags/${id}`);
}
