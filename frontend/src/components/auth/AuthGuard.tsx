"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";

const PUBLIC_ROUTES = ["/login", "/register"];

export function AuthGuard({ children }: { children: React.ReactNode }) {
    const { token } = useAuth();
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        if (!token && !PUBLIC_ROUTES.includes(pathname)) {
            router.push("/login");
        }
        if (token && PUBLIC_ROUTES.includes(pathname)) {
            router.push("/");
        }
    }, [token, pathname, router]);

    // Show children if it's public or we have token
    // In a real app we might want a "loading" state during rehydration
    return <>{children}</>;
}
