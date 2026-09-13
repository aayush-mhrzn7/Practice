import type { Request, Response } from "express";
import prisma from "../../lib/prisma";

// The client sends `skills` as an array, but the column is a single String.
// Normalise in both directions so what we store and what we return stay stable.
function toSkillsColumn(skills: unknown): string | null {
  const parts = Array.isArray(skills)
    ? skills.map((skill) => String(skill))
    : typeof skills === "string"
      ? skills.split(",")
      : [];

  const cleaned = parts.map((skill) => skill.trim()).filter(Boolean);
  return cleaned.length > 0 ? cleaned.join(",") : null;
}

function toSkillsList(skills: string): string[] {
  return skills
    .split(",")
    .map((skill) => skill.trim())
    .filter(Boolean);
}

function isUniqueViolation(error: unknown) {
  return (
    typeof error === "object" &&
    error !== null &&
    (error as { code?: string }).code === "P2002"
  );
}

export async function createTenant(req: Request, res: Response) {
  const { name, bio } = req.body ?? {};
  const skills = toSkillsColumn(req.body?.skills);

  if (
    typeof name !== "string" ||
    !name.trim() ||
    typeof bio !== "string" ||
    !bio.trim() ||
    !skills
  ) {
    res.status(400).json({ error: "Missing required fields" });
    return;
  }

  const slug = name.trim().toLowerCase().replace(/\s+/g, "-");

  const template = await prisma.template.findFirst();
  if (!template) {
    res.status(500).json({ error: "No template found" });
    return;
  }

  try {
    const tenant = await prisma.tenant.create({
      data: {
        slug,
        name: name.trim(),
        bio: bio.trim(),
        skills,
        templateId: template.id,
      },
    });
    res.json({ slug: tenant.slug });
  } catch (error) {
    if (isUniqueViolation(error)) {
      res.status(409).json({ error: `The name "${name.trim()}" is taken` });
      return;
    }
    throw error;
  }
}

export async function getTenant(req: Request, res: Response) {
  const slug = req.params.slug;

  if (!slug) {
    res.status(400).json({ error: "Invalid slug parameter" });
    return;
  }

  const tenant = await prisma.tenant.findUnique({ where: { slug } });
  if (!tenant) {
    res.status(404).json({ error: "Tenant not found" });
    return;
  }

  const template = await prisma.template.findUnique({
    where: { id: tenant.templateId },
  });

  // Hand the client a real array so `skills.map(...)` works on the tenant page.
  res.json({
    tenant: { ...tenant, skills: toSkillsList(tenant.skills) },
    template,
  });
}
