import { apiRequest } from "@/lib/api/client";
import {
  buildStoreNameMap,
  mapBackendUser,
  type BackendStore,
  type BackendUser,
} from "@/lib/api/mappers";
import type { User } from "@/lib/types";

export type OrganizationStatus = "active" | "disabled";

export interface Organization {
  id: string;
  name: string;
  status: OrganizationStatus;
}

interface BackendOrganizationAdminResponse {
  id: string;
  name: string;
  status: OrganizationStatus;
}

export type CreateOrganizationData = {
  id: string;
  name: string;
};

function mapOrganization(org: BackendOrganizationAdminResponse): Organization {
  return {
    id: org.id,
    name: org.name,
    status: org.status,
  };
}

export async function listOrganizations(): Promise<Organization[]> {
  const rows = await apiRequest<BackendOrganizationAdminResponse[]>(
    "/api/organizations",
  );
  return rows.map(mapOrganization);
}

export async function getOrganization(id: string): Promise<Organization> {
  const org = await apiRequest<BackendOrganizationAdminResponse>(
    `/api/organizations/${id}`,
  );
  return mapOrganization(org);
}

export async function getOrgStores(orgId: string): Promise<BackendStore[]> {
  return apiRequest<BackendStore[]>(`/api/organizations/${orgId}/stores`);
}

export async function getOrgUsers(orgId: string): Promise<User[]> {
  const [users, stores] = await Promise.all([
    apiRequest<BackendUser[]>(`/api/organizations/${orgId}/users`),
    getOrgStores(orgId),
  ]);
  const names = buildStoreNameMap(stores);
  return users.map((user) => mapBackendUser(user, names));
}

export async function createOrganization(
  data: CreateOrganizationData,
): Promise<Organization> {
  const created = await apiRequest<BackendOrganizationAdminResponse>(
    "/api/organizations",
    {
      method: "POST",
      body: {
        id: data.id,
        name: data.name,
      },
    },
  );
  return mapOrganization(created);
}

export async function toggleOrganization(id: string): Promise<Organization> {
  const updated = await apiRequest<BackendOrganizationAdminResponse>(
    `/api/organizations/${id}/toggle`,
    { method: "POST" },
  );
  return mapOrganization(updated);
}

export async function deleteOrganization(
  id: string,
  confirm: string,
): Promise<void> {
  await apiRequest<void>(`/api/organizations/${id}`, {
    method: "DELETE",
    body: { confirm },
  });
}
