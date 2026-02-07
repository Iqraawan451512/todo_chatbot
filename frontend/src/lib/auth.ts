/**
 * Better Auth client configuration.
 *
 * Better Auth is a TypeScript authentication framework.
 * This module sets up the auth client for the frontend.
 * In development, authentication is bypassed with a hardcoded user ID.
 */

// Placeholder for Better Auth integration.
// In production, configure with:
//
// import { createAuthClient } from "better-auth/client";
//
// export const authClient = createAuthClient({
//   baseURL: process.env.NEXT_PUBLIC_AUTH_URL || "http://localhost:3000",
// });

export function getCurrentUserId(): string {
  // In production, this would return the authenticated user's ID
  // from Better Auth session.
  return "dev-user";
}
