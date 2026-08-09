import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { TopNav } from "@/components/dashboard/top-nav";

const { useAuthMock } = vi.hoisted(() => ({
  useAuthMock: vi.fn(),
}));

vi.mock("next/link", () => ({
  default: ({
    children,
    href,
    ...props
  }: {
    children: React.ReactNode;
    href: string;
  }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
}));

vi.mock("@/lib/api/alerts", () => ({
  getOpenAlertCount: vi.fn().mockResolvedValue(0),
  subscribeOpenAlertCount: vi.fn().mockReturnValue(() => undefined),
}));

vi.mock("@/components/dashboard/organization-label", () => ({
  OrganizationLabel: () => <span>Org</span>,
}));

vi.mock("@/components/dashboard/user-menu", () => ({
  UserMenu: () => <span>User menu</span>,
}));

vi.mock("@/lib/auth/AuthContext", () => ({
  useAuth: () => useAuthMock(),
}));

describe("TopNav admin links", () => {
  beforeEach(() => {
    useAuthMock.mockReset();
  });

  afterEach(() => {
    cleanup();
  });

  it("shows Admin nav for System Administrator", () => {
    useAuthMock.mockReturnValue({
      user: { role: "System Administrator", name: "Admin", email: "a@test" },
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    render(<TopNav />);

    expect(screen.getByText("Admin")).toBeInTheDocument();
  });

  it("hides Admin nav for Retail Analyst", () => {
    useAuthMock.mockReturnValue({
      user: { role: "Retail Analyst", name: "User", email: "u@test" },
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
    });

    render(<TopNav />);

    expect(screen.queryByText("Admin")).not.toBeInTheDocument();
    expect(screen.getByText("Reports")).toBeInTheDocument();
  });
});
