import { describe, expect, it } from "vitest";

import { ApiClientError } from "@/lib/api/client";
import { getLoginErrorMessage } from "@/lib/api/auth";

describe("getLoginErrorMessage", () => {
  it("shows a distinct message for disabled accounts", () => {
    const error = new ApiClientError("Account disabled", "account_disabled", 401);

    expect(getLoginErrorMessage(error)).toBe(
      "This account has been disabled. Contact an administrator.",
    );
  });

  it("keeps the generic message for invalid credentials", () => {
    const error = new ApiClientError(
      "Invalid email or password",
      "invalid_credentials",
      401,
    );

    expect(getLoginErrorMessage(error)).toBe("Invalid email or password.");
  });

  it("keeps the generic message for unknown errors", () => {
    expect(getLoginErrorMessage(new Error("network failure"))).toBe(
      "Invalid email or password.",
    );
  });
});
