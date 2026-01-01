import { Outlet } from "react-router-dom";

import { CNavbar } from "@/components/navbar";
export default function MainLayout() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-foreground">
      <CNavbar />

      <main className="container mx-auto max-w-7xl p-6">
        <Outlet />
      </main>
    </div>
  );
}
