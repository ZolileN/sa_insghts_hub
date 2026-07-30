"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { LiboLogo } from "@/components/brand/libo-logo";
import {
  ContactModalTrigger,
  PricingModalTrigger,
} from "@/components/marketing/marketing-modals";

export function MarketingFooter() {
  return (
    <footer className="border-t border-[var(--border)] px-6 py-10 lg:px-10">
      <div className="mx-auto flex max-w-7xl flex-col items-start justify-between gap-6 sm:flex-row sm:items-center">
        <LiboLogo href="/" showWordmark size="lg" />
        <div className="flex flex-wrap gap-6 text-sm text-[var(--muted-foreground)]">
          <Link href="/dashboard/crime" className="hover:text-[var(--foreground)]">
            Dashboard
          </Link>
          <Link href="#topics" className="hover:text-[var(--foreground)]">Topics</Link>
          <PricingModalTrigger className="hover:text-[var(--foreground)]">
            Pricing
          </PricingModalTrigger>
          <ContactModalTrigger className="hover:text-[var(--foreground)]">
            Contact
          </ContactModalTrigger>
        </div>
        <p className="font-mono text-xs text-[var(--muted-foreground)]">
          Built by{" "}
          <a
            href="https://www.mlkcomputer.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[var(--foreground)] hover:text-[var(--primary)]"
          >
            MLK Computer Consulting
          </a>
        </p>
      </div>
    </footer>
  );
}
