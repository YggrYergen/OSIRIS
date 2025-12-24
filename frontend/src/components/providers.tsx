"use client";

import { GoogleOAuthProvider } from "@react-oauth/google";

export function Providers({ children }: { children: React.ReactNode }) {
    const CLIENT_ID = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

    if (!CLIENT_ID) {
        console.warn("Google Client ID not found in environment variables");
        // We render children anyway so the app doesn't crash, but Auth won't work
        return <>{children}</>;
    }

    return (
        <GoogleOAuthProvider clientId={CLIENT_ID}>
            {children}
        </GoogleOAuthProvider>
    );
}
