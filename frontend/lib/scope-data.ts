import type { Organization, ScopeCamera, ScopeZone } from "@/lib/types";

function zones(...names: string[]): ScopeZone[] {
  return names.map((name, i) => ({ id: `${i}-${name}`, name }));
}

/** Fixed org id for this single-tenant deployment. */
export const DEPLOYMENT_ORG_ID = "org-northwind";

/**
 * Single organization for this deployment. Store → Camera → Zone hierarchy only;
 * there is no org switcher in the UI.
 */
export const DEPLOYMENT_ORGANIZATION: Organization = {
  id: DEPLOYMENT_ORG_ID,
  name: "Northwind Retail Group",
  stores: [
    {
      id: "store-downtown",
      name: "Downtown Flagship",
      cameras: [
        {
          id: "cam-entrance",
          name: "Entrance Cam",
          zones: zones("Vestibule", "Greeter Area"),
        },
        {
          id: "cam-checkout",
          name: "Checkout Cam",
          zones: zones("Registers", "Queue Lane"),
        },
        {
          id: "cam-apparel",
          name: "Apparel Cam",
          zones: zones("Menswear", "Womenswear", "Fitting Rooms"),
        },
      ],
    },
    {
      id: "store-mall",
      name: "Riverside Mall",
      cameras: [
        {
          id: "cam-atrium",
          name: "Atrium Cam",
          zones: zones("Main Aisle", "Promo Display"),
        },
        {
          id: "cam-electronics",
          name: "Electronics Cam",
          zones: zones("TVs", "Mobile", "Accessories"),
        },
      ],
    },
    {
      id: "store-westside",
      name: "Westside Market",
      cameras: [
        {
          id: "cam-produce",
          name: "Produce Cam",
          zones: zones("Fresh Produce", "Floral"),
        },
        {
          id: "cam-deli",
          name: "Deli Cam",
          zones: zones("Deli Counter", "Bakery"),
        },
      ],
    },
  ],
};

/** @deprecated Internal compatibility — always a single org. */
export const ORGANIZATIONS: Organization[] = [DEPLOYMENT_ORGANIZATION];
