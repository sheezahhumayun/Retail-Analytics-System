import { apiRequest } from "@/lib/api/client";
import type { BackendStore } from "@/lib/api/mappers";

export type CreateStoreData = {
  id: string;
  org_id: string;
  name: string;
  address?: string | null;
};

export type UpdateStoreData = {
  name?: string;
  address?: string | null;
};

export async function createStore(data: CreateStoreData): Promise<BackendStore> {
  return apiRequest<BackendStore>("/api/stores", {
    method: "POST",
    body: {
      id: data.id,
      org_id: data.org_id,
      name: data.name,
      address: data.address ?? null,
    },
  });
}

export async function updateStore(
  storeId: string,
  data: UpdateStoreData,
): Promise<BackendStore> {
  const body: Record<string, unknown> = {};
  if (data.name !== undefined) body.name = data.name;
  if (data.address !== undefined) body.address = data.address;

  return apiRequest<BackendStore>(`/api/stores/${storeId}`, {
    method: "PUT",
    body,
  });
}

export async function deleteStore(storeId: string): Promise<void> {
  await apiRequest<void>(`/api/stores/${storeId}`, { method: "DELETE" });
}
