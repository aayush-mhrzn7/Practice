export type User = {
  id: number;
  email: string;
  name: string;
  bio: string | null;
  created_at: string;
  updated_at: string;
};

export type AuthTokens = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export type Tag = {
  id: number;
  name: string;
  created_at: string | null;
  updated_at: string | null;
};

export type Bookmark = {
  id: number;
  url: string;
  title: string;
  notes: string | null;
  user_id: number;
  tags: Tag[];
  created_at: string;
  updated_at: string;
};

export type Paginated<T> = {
  data: T[];
  total: number;
  page: number;
  page_size: number;
};

export type BookmarkDraft = {
  url: string;
  title: string;
  notes?: string | null;
};
