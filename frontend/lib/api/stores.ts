// MOCK IMPLEMENTATION — swap the function bodies below for real fetch() calls
// to the FastAPI backend when Module 12 is live. Signatures and return types
// must not change.

import {
  DEPLOYMENT_ORGANIZATION,
  ORGANIZATIONS,
} from "@/lib/scope-data";
import type { Organization, Store } from "@/lib/types";

/** Returns the deployment's single organization (store → camera → zone tree). */
export function getOrganization(): Promise<Organization> {
  return Promise.resolve(DEPLOYMENT_ORGANIZATION);
}

/** Returns all stores for the deployment organization. */
export function getStores(): Promise<Store[]> {
  return Promise.resolve([...DEPLOYMENT_ORGANIZATION.stores]);
}

/**
 * @deprecated Single-tenant deployment — use `getOrganization()` instead.
 * Returns a one-element array for backwards compatibility.
 */
export function getOrganizations(): Promise<Organization[]> {
  return Promise.resolve(ORGANIZATIONS);
}
