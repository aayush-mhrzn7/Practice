import { http } from "@/lib/api/client";
import { setTokens } from "@/lib/auth/storage";
import type { AuthTokens, User } from "@/lib/types";

export async function login(email: string, password: string) {
  const { data } = await http.post<AuthTokens>("/users/login", { email, password });
  setTokens(data.access_token, data.refresh_token);
  return data;
}

export async function signup(payload: {
  email: string;
  password: string;
  name: string;
  bio?: string;
}) {
  const { data } = await http.post<User>("/users/signup", payload);
  return data;
}

export async function getMe() {
  const { data } = await http.get<User>("/users/me");
  return data;
}
