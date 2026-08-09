import { apiRequest } from "@/lib/api/client";
import {
  buildStoreNameMap,
  frontendRoleToBackend,
  frontendStatusToBackend,
  mapBackendUser,
  type BackendStore,
  type BackendUser,
} from "@/lib/api/mappers";
import { getSessionOrgId } from "@/lib/api/auth";
import {
  ROLE_COLORS,
  USER_ROLES,
  getRoleColor,
  getStatusColor,
} from "@/lib/admin-users-data";
import type { User, UserRole, UserStatus } from "@/lib/types";

export { ROLE_COLORS, USER_ROLES, getRoleColor, getStatusColor };

/** Hydrated from GET /api/stores — populated on first users API call. */
export const STORES: string[] = [];

export type CreateUserData = {
  name: string;
  email: string;
  role: UserRole;
  assignedStore: string;
  status?: UserStatus;
  password: string;
  id?: string;
};

export type UpdateUserData = Partial<
  Pick<User, "name" | "email" | "role" | "assignedStore" | "status">
>;

export type ResetPasswordResult = {
  user_id: string;
  success: boolean;
};

let storeNameMap: Map<string, string> | null = null;

async function ensureStoreNames(): Promise<Map<string, string>> {
  if (storeNameMap) return storeNameMap;
  const stores = await apiRequest<BackendStore[]>("/api/stores");
  storeNameMap = buildStoreNameMap(stores);
  STORES.length = 0;
  STORES.push(...stores.map((store) => store.name));
  return storeNameMap;
}

async function resolveStoreId(storeName: string): Promise<string | null> {
  const stores = await apiRequest<BackendStore[]>("/api/stores");
  return stores.find((store) => store.name === storeName)?.id ?? null;
}

function slugifyId(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .slice(0, 64);
}

export async function getUsers(): Promise<User[]> {
  const [users, names] = await Promise.all([
    apiRequest<BackendUser[]>("/api/users"),
    ensureStoreNames(),
  ]);
  return users.map((user) => mapBackendUser(user, names));
}

export async function createUser(data: CreateUserData): Promise<User> {
  const org_id = getSessionOrgId();
  if (!org_id) {
    throw new Error("Not authenticated");
  }
  const store_id = await resolveStoreId(data.assignedStore);
  const created = await apiRequest<BackendUser>("/api/users", {
    method: "POST",
    body: {
      id: data.id ?? slugifyId(data.email.split("@")[0] || data.name),
      email: data.email,
      name: data.name,
      role: frontendRoleToBackend(data.role),
      org_id,
      store_id,
      password: data.password,
    },
  });
  const names = await ensureStoreNames();
  return mapBackendUser(created, names);
}

export async function updateUser(
  id: string,
  data: UpdateUserData,
): Promise<User> {
  const body: Record<string, unknown> = {};
  if (data.name !== undefined) body.name = data.name;
  if (data.email !== undefined) body.email = data.email;
  if (data.role !== undefined) body.role = frontendRoleToBackend(data.role);
  if (data.assignedStore !== undefined) {
    body.store_id = await resolveStoreId(data.assignedStore);
  }
  if (data.status !== undefined) {
    body.status = frontendStatusToBackend(data.status);
  }

  const updated = await apiRequest<BackendUser>(`/api/users/${id}`, {
    method: "PUT",
    body,
  });
  const names = await ensureStoreNames();
  return mapBackendUser(updated, names);
}

export async function deleteUser(id: string): Promise<boolean> {
  try {
    await apiRequest<void>(`/api/users/${id}`, { method: "DELETE" });
    return true;
  } catch {
    return false;
  }
}

export async function resetPassword(
  id: string,
  newPassword: string,
): Promise<ResetPasswordResult> {
  try {
    await apiRequest<void>(`/api/users/${id}/reset-password`, {
      method: "POST",
      body: { new_password: newPassword },
    });
    return { user_id: id, success: true };
  } catch {
    return { user_id: id, success: false };
  }
}
