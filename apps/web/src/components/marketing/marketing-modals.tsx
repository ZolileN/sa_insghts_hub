"use client";

import {
  createContext,
  useCallback,
  useContext,
  useState,
  type ReactNode,
} from "react";
import Link from "next/link";
import { ArrowRight, Mail, MapPin, Phone } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { PRICING_PLANS } from "@/shared/marketing/content";
import {
  buildHelloMailto,
  MLK_HELLO_EMAIL,
} from "@/shared/marketing/mailto";
import { cn } from "@/shared/utils";

const CONTACT_MAILTO = buildHelloMailto("contact");

type ModalId = "contact" | "pricing" | null;

type MarketingModalsContextValue = {
  openContact: () => void;
  openPricing: () => void;
};

const MarketingModalsContext = createContext<MarketingModalsContextValue | null>(
  null,
);

export function useMarketingModals() {
  const ctx = useContext(MarketingModalsContext);
  if (!ctx) {
    throw new Error("useMarketingModals must be used within MarketingModalsProvider");
  }
  return ctx;
}

export function MarketingModalsProvider({ children }: { children: ReactNode }) {
  const [active, setActive] = useState<ModalId>(null);

  const openContact = useCallback(() => setActive("contact"), []);
  const openPricing = useCallback(() => setActive("pricing"), []);

  return (
    <MarketingModalsContext.Provider value={{ openContact, openPricing }}>
      {children}

      <Dialog
        open={active === "contact"}
        onOpenChange={(open) => setActive(open ? "contact" : null)}
      >
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Get in touch</DialogTitle>
            <DialogDescription>
              Questions about Libo Insights, Pro access, or enterprise plans? Reach
              MLK Computer Consulting — we&apos;ll get back to you shortly.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <a
              href={CONTACT_MAILTO}
              className="flex items-start gap-3 rounded-lg border border-[var(--border)] p-4 transition-colors hover:bg-[var(--accent)]/50"
            >
              <Mail className="mt-0.5 h-4 w-4 shrink-0 text-[var(--primary)]" />
              <div>
                <p className="text-sm font-medium">Email</p>
                <p className="text-sm text-[var(--muted-foreground)]">
                  {MLK_HELLO_EMAIL}
                </p>
              </div>
            </a>
            <a
              href="tel:+27825319901"
              className="flex items-start gap-3 rounded-lg border border-[var(--border)] p-4 transition-colors hover:bg-[var(--accent)]/50"
            >
              <Phone className="mt-0.5 h-4 w-4 shrink-0 text-[var(--primary)]" />
              <div>
                <p className="text-sm font-medium">Phone</p>
                <p className="text-sm text-[var(--muted-foreground)]">
                  +27 82 531 9901
                </p>
              </div>
            </a>
            <div className="flex items-start gap-3 rounded-lg border border-[var(--border)] p-4">
              <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-[var(--primary)]" />
              <div>
                <p className="text-sm font-medium">Office</p>
                <p className="text-sm text-[var(--muted-foreground)]">
                  The Lookout Hill, Khayelitsha, Cape Town
                </p>
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-2 sm:flex-row">
            <Button className="flex-1" asChild>
              <a href={CONTACT_MAILTO}>
                Send email
                <ArrowRight className="h-4 w-4" />
              </a>
            </Button>
            <Button className="flex-1" variant="outline" asChild>
              <a
                href="https://www.mlkcomputer.com/"
                target="_blank"
                rel="noopener noreferrer"
              >
                Visit MLK Computer
              </a>
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog
        open={active === "pricing"}
        onOpenChange={(open) => setActive(open ? "pricing" : null)}
      >
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Pricing</DialogTitle>
            <DialogDescription>
              Start free on all dashboards. Upgrade when you need AI analyst, exports,
              and team features.
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 sm:grid-cols-3">
            {PRICING_PLANS.map((plan) => (
              <div
                key={plan.tier}
                className={cn(
                  "relative flex flex-col rounded-lg border border-[var(--border)] p-4",
                  plan.featured && "border-[var(--primary)] ring-1 ring-[var(--primary)]/20",
                )}
              >
                {plan.featured && "badge" in plan && plan.badge && (
                  <Badge className="mb-2" variant="default">
                    {plan.badge}
                  </Badge>
                )}
                <p className="text-sm font-semibold text-[var(--muted-foreground)]">
                  {plan.tier}
                </p>
                <p className="mt-1 text-2xl font-bold tracking-tight">
                  {plan.price}
                  {"priceSuffix" in plan && plan.priceSuffix && (
                    <span className="text-sm font-normal text-[var(--muted-foreground)]">
                      {plan.priceSuffix}
                    </span>
                  )}
                </p>
                <p className="mt-1 text-xs text-[var(--muted-foreground)]">
                  {plan.period}
                </p>
                <ul className="mt-4 flex-1 space-y-1.5 text-xs">
                  {plan.features.slice(0, 4).map((f) => (
                    <li key={f.text} className="flex gap-1.5">
                      <span
                        className={
                          f.included ? "text-[var(--success)]" : "text-[var(--muted-foreground)]"
                        }
                      >
                        {f.included ? "✓" : "—"}
                      </span>
                      <span
                        className={cn(!f.included && "text-[var(--muted-foreground)]")}
                      >
                        {f.text}
                      </span>
                    </li>
                  ))}
                </ul>
                {plan.href.startsWith("/") ? (
                  <Button
                    className="mt-4 w-full"
                    size="sm"
                    variant={plan.primary ? "default" : "outline"}
                    asChild
                  >
                    <Link href={plan.href}>{plan.cta}</Link>
                  </Button>
                ) : (
                  <Button
                    className="mt-4 w-full"
                    size="sm"
                    variant={plan.primary ? "default" : "outline"}
                    asChild
                  >
                    <a href={plan.href}>{plan.cta}</a>
                  </Button>
                )}
              </div>
            ))}
          </div>

          <p className="text-center text-xs text-[var(--muted-foreground)]">
            See full feature lists on the{" "}
            <button
              type="button"
              className="text-[var(--primary)] underline-offset-2 hover:underline"
              onClick={() => {
                setActive(null);
                document.getElementById("pricing")?.scrollIntoView({ behavior: "smooth" });
              }}
            >
              pricing section
            </button>
            .
          </p>
        </DialogContent>
      </Dialog>
    </MarketingModalsContext.Provider>
  );
}

export function ContactModalTrigger({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  const { openContact } = useMarketingModals();
  return (
    <button type="button" className={className} onClick={openContact}>
      {children}
    </button>
  );
}

export function PricingModalTrigger({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  const { openPricing } = useMarketingModals();
  return (
    <button type="button" className={className} onClick={openPricing}>
      {children}
    </button>
  );
}
