import type { AppProps } from "next/app";
import { useRouter } from "next/router";
import "../app/globals.css";
import AdminShell from "../components/layout/AdminShell";
import { AdminGuard, AuthProvider } from "../services/AuthProvider";

export default function AdminPagesApp({ Component, pageProps }: AppProps) {
  const router = useRouter();
  const isLoginPage = router.pathname === "/login";

  return (
    <AuthProvider>
      <AdminGuard>
        {isLoginPage ? (
          <Component {...pageProps} />
        ) : (
          <AdminShell>
            <Component {...pageProps} />
          </AdminShell>
        )}
      </AdminGuard>
    </AuthProvider>
  );
}
