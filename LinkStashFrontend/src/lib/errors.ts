import { isAxiosError } from "axios";

type ValidationBody = {
  error?: { message?: string; details?: { field: string; message: string }[] };
  detail?: string | { msg?: string }[];
};

export function getErrorMessage(error: unknown): string {
  if (!isAxiosError(error)) {
    return error instanceof Error ? error.message : "Something went wrong";
  }

  const data = error.response?.data as ValidationBody | undefined;
  if (!data) return error.message;

  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail) && data.detail[0]?.msg) return data.detail[0].msg;
  if (data.error?.details?.[0]?.message) {
    return data.error.details[0].message;
  }
  if (data.error?.message) return data.error.message;

  return error.message || "Request failed";
}
