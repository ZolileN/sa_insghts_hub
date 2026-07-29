import Image from "next/image";
import Link from "next/link";
import { cn } from "@/shared/utils";

type LiboLogoProps = {
  className?: string;
  showWordmark?: boolean;
  href?: string;
  size?: "sm" | "md" | "lg";
};

const MARK_SIZES = {
  sm: { w: 22, h: 27 },
  md: { w: 28, h: 34 },
  lg: { w: 36, h: 44 },
} as const;

export function LiboLogo({
  className,
  showWordmark = false,
  href,
  size = "md",
}: LiboLogoProps) {
  const dims = MARK_SIZES[size];
  const src = showWordmark ? "/libo-logo.svg" : "/libo-mark.svg";
  const width = showWordmark ? 200 : dims.w;
  const height = showWordmark ? 48 : dims.h;

  const content = (
    <span className={cn("inline-flex items-center gap-2.5", className)}>
      <Image
        src={src}
        alt="Libo Insights"
        width={width}
        height={height}
        className={cn(showWordmark ? "h-10 w-auto" : "shrink-0")}
        priority
      />
      {!showWordmark && (
        <span className="inline-flex flex-col leading-none">
          <span className="text-sm font-semibold tracking-tight text-[var(--foreground)]">
            Libo <span className="font-normal text-[var(--primary)]">Insights</span>
          </span>
          <span className="mt-1 text-[9px] uppercase tracking-[0.14em] text-[var(--muted-foreground)]">
            Area intelligence
          </span>
        </span>
      )}
    </span>
  );

  if (href) {
    return (
      <Link href={href} className="inline-flex items-center">
        {content}
      </Link>
    );
  }

  return content;
}

export function LiboMark({
  className,
  size = 24,
}: {
  className?: string;
  size?: number;
}) {
  return (
    <Image
      src="/libo-mark.svg"
      alt=""
      width={size}
      height={Math.round(size * 1.24)}
      className={cn("shrink-0", className)}
      aria-hidden
    />
  );
}
