export type PermissionCode =
  | "documents:read"
  | "documents:write"
  | "documents:edit"
  | "documents:delete"
  | "notes:read"
  | "notes:write"
  | "notes:edit"
  | "notes:delete"
  | "announcements:read"
  | "announcements:write"
  | "announcements:edit"
  | "announcements:delete"
  | "audit:read"
  | "settings:read"
  | "settings:edit";

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

export type TitledOut = {
  id: number;
  title: string;
  body: string;
  owner_id: number;
  created_at: string;
};

export type DocumentOut = TitledOut;

export type PermissionItem = {
  code: string;
  label: string;
};

export type PermissionGroup = {
  key: string;
  label: string;
  permissions: PermissionItem[];
};

export type AuditEvent = {
  id: number;
  actor_id: number | null;
  action: string;
  detail: string;
  created_at: string;
};

export type SettingOut = {
  workspace_name: string;
  banner: string;
};
