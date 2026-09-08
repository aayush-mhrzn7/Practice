/** types.ts — JSON shapes matching api/schemas.py. */
export type UserMe = {
  id: number;
  email: string;
  is_admin: boolean;
  permissions: string[];
};

export type TokenOut = {
  access_token: string;
};

export type RoleBrief = {
  id: number;
  name: string;
};

export type UserList = {
  id: number;
  email: string;
  is_admin: boolean;
  roles: RoleBrief[];
};

export type RoleOut = {
  id: number;
  name: string;
  permissions: string[];
};

export type DocumentOut = {
  id: number;
  title: string;
  body: string;
  owner_id: number;
  created_at: string;
};

export type AuditEvent = {
  id: number;
  actor_id: number | null;
  action: string;
  detail: string;
  created_at: string;
};
