export const MLK_HELLO_EMAIL = "hello@mlkcomputer.com";

export type MailtoIntent = "contact" | "pro" | "business";

const MAILTO_TEMPLATES: Record<MailtoIntent, { subject: string; body: string }> = {
  contact: {
    subject: "Libo Insights — general enquiry",
    body: [
      "Hi MLK Computer Consulting,",
      "",
      "I'd like to get in touch about Libo Insights.",
      "",
      "Name:",
      "Organisation:",
      "Email:",
      "",
      "Message:",
      "",
      "Thanks,",
    ].join("\n"),
  },
  pro: {
    subject: "Libo Insights — Pro plan trial request",
    body: [
      "Hi MLK Computer Consulting,",
      "",
      "I'm interested in starting a Libo Insights Pro trial (R199/mo).",
      "",
      "Name:",
      "Organisation:",
      "Email:",
      "Phone:",
      "",
      "Please let me know the next steps to activate my trial.",
      "",
      "Thanks,",
    ].join("\n"),
  },
  business: {
    subject: "Libo Insights — Business plan access request",
    body: [
      "Hi MLK Computer Consulting,",
      "",
      "I'm interested in Libo Insights Business (R899/mo — 5 seats, API access).",
      "",
      "Name:",
      "Organisation:",
      "Email:",
      "Phone:",
      "Team size:",
      "Use case:",
      "",
      "Please share onboarding and pricing details for our team.",
      "",
      "Thanks,",
    ].join("\n"),
  },
};

export function buildHelloMailto(intent: MailtoIntent): string {
  const { subject, body } = MAILTO_TEMPLATES[intent];
  const params = new URLSearchParams({
    subject,
    body,
  });
  return `mailto:${MLK_HELLO_EMAIL}?${params.toString()}`;
}
