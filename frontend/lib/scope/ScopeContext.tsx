"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { getOrganization } from "@/lib/api/stores";
import { DEPLOYMENT_ORG_ID } from "@/lib/scope-data";
import { getStoreCameraIds } from "@/lib/scope/scope-filters";
import type {
  Organization,
  ScopeCamera,
  ScopeZone,
  Store,
} from "@/lib/types";

export type ScopeContextValue = {
  isLoading: boolean;
  /** Fixed org id for this deployment — not user-selectable. */
  orgId: string;
  organization: Organization | null;
  storeId: string | null;
  cameraId: string | null;
  zoneId: string | null;
  store: Store | null;
  camera: ScopeCamera | null;
  zone: ScopeZone | null;
  storeCameraIds: string[];
  setStoreId: (id: string) => void;
  setCameraId: (id: string | null) => void;
  setZoneId: (id: string | null) => void;
};

const ScopeContext = createContext<ScopeContextValue | null>(null);

export function ScopeProvider({ children }: { children: ReactNode }) {
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [storeId, setStoreIdState] = useState<string | null>(null);
  const [cameraId, setCameraIdState] = useState<string | null>(null);
  const [zoneId, setZoneIdState] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const org = await getOrganization();
        if (cancelled) return;

        setOrganization(org);
        setStoreIdState(org.stores[0]?.id ?? null);
        setCameraIdState(null);
        setZoneIdState(null);
      } catch {
        if (!cancelled) {
          setOrganization(null);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const orgId = organization?.id ?? DEPLOYMENT_ORG_ID;

  const store = useMemo(
    () => organization?.stores.find((item) => item.id === storeId) ?? null,
    [organization, storeId],
  );

  const camera = useMemo(
    () => store?.cameras.find((item) => item.id === cameraId) ?? null,
    [store, cameraId],
  );

  const zone = useMemo(
    () => camera?.zones.find((item) => item.id === zoneId) ?? null,
    [camera, zoneId],
  );

  const storeCameraIds = useMemo(() => getStoreCameraIds(store), [store]);

  const setStoreId = useCallback((id: string) => {
    setStoreIdState(id);
    setCameraIdState(null);
    setZoneIdState(null);
  }, []);

  const setCameraId = useCallback((id: string | null) => {
    setCameraIdState(id);
    setZoneIdState(null);
  }, []);

  const setZoneId = useCallback((id: string | null) => {
    setZoneIdState(id);
  }, []);

  const value = useMemo<ScopeContextValue>(
    () => ({
      isLoading,
      orgId,
      organization,
      storeId,
      cameraId,
      zoneId,
      store,
      camera,
      zone,
      storeCameraIds,
      setStoreId,
      setCameraId,
      setZoneId,
    }),
    [
      isLoading,
      orgId,
      organization,
      storeId,
      cameraId,
      zoneId,
      store,
      camera,
      zone,
      storeCameraIds,
      setStoreId,
      setCameraId,
      setZoneId,
    ],
  );

  return (
    <ScopeContext.Provider value={value}>{children}</ScopeContext.Provider>
  );
}

export function useScope(): ScopeContextValue {
  const context = useContext(ScopeContext);
  if (!context) {
    throw new Error("useScope must be used within a ScopeProvider");
  }
  return context;
}
