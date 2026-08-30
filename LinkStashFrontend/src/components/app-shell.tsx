"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Bookmark, LogOut, Menu, Tags } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";
import { useSession } from "@/lib/auth/session";
import { cn } from "@/lib/utils";

const nav = [
  { href: "/bookmarks", label: "Bookmarks", icon: Bookmark },
  { href: "/tags", label: "Tags", icon: Tags },
];

function NavLinks({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col gap-1">
      {nav.map((item) => {
        const active = pathname.startsWith(item.href);
        const Icon = item.icon;
        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onNavigate}
            className={cn(
              "group flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-all duration-200",
              active
                ? "bg-primary/15 text-primary shadow-[inset_0_0_0_1px_oklch(0.78_0.12_70_/_0.25)]"
                : "text-muted-foreground hover:bg-muted/70 hover:text-foreground",
            )}
          >
            <Icon
              className={cn(
                "size-4 transition-transform duration-200 group-hover:scale-110",
                active && "text-primary",
              )}
            />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, status, logout } = useSession();
  const router = useRouter();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (status === "ready" && !user) {
      router.replace("/login");
    }
  }, [status, user, router]);

  if (status === "loading" || !user) {
    return (
      <div className="flex min-h-svh items-center justify-center">
        <div className="flex w-64 flex-col gap-3">
          <Skeleton className="h-8 w-40" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-svh">
      <aside className="hidden w-60 shrink-0 border-r border-border/80 bg-sidebar/80 p-4 md:flex md:flex-col">
        <Link href="/bookmarks" className="mb-6 flex items-center gap-2 px-1">
          <span className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-sm transition-transform duration-200 hover:scale-105">
            <Bookmark className="size-4" />
          </span>
          <div>
            <p className="text-sm font-semibold tracking-tight">LinkStash</p>
            <p className="text-[11px] text-muted-foreground">Your quiet library</p>
          </div>
        </Link>
        <NavLinks />
        <div className="mt-auto space-y-3 pt-6">
          <Separator />
          <div className="flex items-center justify-between gap-2 px-1">
            <div className="min-w-0">
              <p className="truncate text-sm font-medium">{user.name}</p>
              <p className="truncate text-xs text-muted-foreground">{user.email}</p>
            </div>
            <Button variant="ghost" size="icon-sm" onClick={logout} aria-label="Log out">
              <LogOut className="size-4" />
            </Button>
          </div>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-border/80 px-4 py-3 md:hidden">
          <div className="flex items-center gap-2">
            <span className="flex size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <Bookmark className="size-4" />
            </span>
            <span className="text-sm font-semibold">LinkStash</span>
          </div>
          <Sheet open={open} onOpenChange={setOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon-sm" aria-label="Open menu">
                <Menu className="size-4" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-64">
              <SheetHeader>
                <SheetTitle>LinkStash</SheetTitle>
              </SheetHeader>
              <div className="px-2">
                <NavLinks onNavigate={() => setOpen(false)} />
                <Separator className="my-4" />
                <p className="px-3 text-sm font-medium">{user.name}</p>
                <p className="px-3 text-xs text-muted-foreground">{user.email}</p>
                <Button variant="ghost" className="mt-3 w-full justify-start" onClick={logout}>
                  <LogOut className="size-4" />
                  Log out
                </Button>
              </div>
            </SheetContent>
          </Sheet>
        </header>
        <main className="flex-1 px-4 py-6 sm:px-8">{children}</main>
      </div>
    </div>
  );
}
