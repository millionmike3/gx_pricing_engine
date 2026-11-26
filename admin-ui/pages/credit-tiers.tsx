import { useEffect, useState } from "react";
import Button from "../components/UI/Button";
import Input from "../components/UI/Input";
import { api } from "../services/api";

type Tier = {
  range: string;
  adjustment: number | string;
};

type TierSection = "fico" | "ltv";

type PricingMatrix = {
  pricingTiers: {
    fico: Tier[];
    ltv: Tier[];
    [key: string]: unknown;
  };
  [key: string]: any;
};

export default function CreditTiers() {
  const [matrix, setMatrix] = useState<PricingMatrix | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    let active = true;

    async function loadMatrix() {
      try {
        setLoading(true);
        setError("");

        const response = await api.get<PricingMatrix>("/admin/matrix");

        if (active) {
          setMatrix(response.data);
        }
      } catch (err: unknown) {
        const message =
          (err as { response?: { data?: { detail?: string } }; message?: string })
            ?.response?.data?.detail ||
          (err as { message?: string })?.message ||
          "Unable to load the pricing matrix.";

        if (active) setError(message);
      } finally {
        if (active) setLoading(false);
      }
    }

    loadMatrix();

    return () => {
      active = false;
    };
  }, []);

  function updateAdjustment(
    section: TierSection,
    index: number,
    value: string
  ) {
    setSuccess("");
    setError("");

    setMatrix((current) => {
      if (!current) return current;

      return {
        ...current,
        pricingTiers: {
          ...current.pricingTiers,
          [section]: current.pricingTiers[section].map((tier, tierIndex) =>
            tierIndex === index
              ? { ...tier, adjustment: value }
              : tier
          ),
        },
      };
    });
  }

  async function saveMatrix() {
    if (!matrix) return;

    const sections: TierSection[] = ["fico", "ltv"];

    for (const section of sections) {
      for (const tier of matrix.pricingTiers[section]) {
        if (
          tier.adjustment === "" ||
          !Number.isFinite(Number(tier.adjustment))
        ) {
          setError(`Enter a valid numeric adjustment for ${section.toUpperCase()} range ${tier.range}.`);
          return;
        }
      }
    }

    if (!window.confirm(
      "Save these FICO and LTV adjustments to the live pricing matrix?"
    )) {
      return;
    }

    try {
      setSaving(true);
      setError("");
      setSuccess("");

      const updatedMatrix = {
        ...matrix,
        pricingTiers: {
          ...matrix.pricingTiers,
          fico: matrix.pricingTiers.fico.map((tier) => ({
            ...tier,
            adjustment: Number(tier.adjustment),
          })),
          ltv: matrix.pricingTiers.ltv.map((tier) => ({
            ...tier,
            adjustment: Number(tier.adjustment),
          })),
        },
      };

      const file = new Blob(
        [JSON.stringify(updatedMatrix, null, 2)],
        { type: "application/json" }
      );

      const formData = new FormData();
      formData.append("file", file, "pricing_matrix.json");

      await api.post("/matrix/upload", formData);

      setMatrix(updatedMatrix);
      setSuccess("Pricing matrix saved successfully.");
    } catch (err: unknown) {
      const message =
        (err as { response?: { data?: { detail?: string } }; message?: string })
          ?.response?.data?.detail ||
        (err as { message?: string })?.message ||
        "Unable to save the pricing matrix.";

      setError(message);
    } finally {
      setSaving(false);
    }
  }

  function renderTierSection(section: TierSection, heading: string) {
    const tiers = matrix?.pricingTiers?.[section] ?? [];

    return (
      <section className="mb-8 rounded-lg border border-white/10 bg-white/[0.02] p-5">
        <h2 className="mb-4 text-lg font-semibold text-white">{heading}</h2>

        <div className="mb-3 grid grid-cols-[minmax(0,1fr)_minmax(120px,180px)] gap-4 border-b border-white/10 pb-2 text-sm text-gray-400">
          <span>Range</span>
          <span>Rate adjustment (%)</span>
        </div>

        {tiers.map((tier, index) => (
          <div
            key={`${section}-${tier.range}-${index}`}
            className="grid grid-cols-[minmax(0,1fr)_minmax(120px,180px)] items-center gap-4 border-b border-white/5 py-2 last:border-0"
          >
            <span className="text-sm text-gray-200">{tier.range}</span>
            <Input
              label=""
              type="number"
              value={tier.adjustment}
              onChange={(value) =>
                updateAdjustment(section, index, value)
              }
              className="mb-0"
            />
          </div>
        ))}
      </section>
    );
  }

  if (loading) {
    return <div className="p-6 text-gray-300">Loading live pricing tiers...</div>;
  }

  if (!matrix && error) {
    return (
      <div className="p-6">
        <h1 className="mb-3 text-xl font-semibold text-white">Credit Tiers</h1>
        <p className="text-red-400">{error}</p>
        <Button onClick={() => window.location.reload()}>Retry</Button>
      </div>
    );
  }

  if (!matrix) return null;

  return (
    <main className="space-y-6 p-6 text-white">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Credit Tiers</h1>
          <p className="mt-1 text-sm text-gray-400">
            Live pricing matrix · FICO and loan-to-value adjustments
          </p>
        </div>

        <Button onClick={saveMatrix} disabled={saving}>
          {saving ? "Saving..." : "Save Matrix"}
        </Button>
      </div>

      {error && (
        <div role="alert" className="rounded border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300">
          {error}
        </div>
      )}

      {success && (
        <div role="status" className="rounded border border-green-500/30 bg-green-500/10 p-3 text-sm text-green-300">
          {success}
        </div>
      )}

      {renderTierSection("fico", "FICO Credit Adjustments")}
      {renderTierSection("ltv", "LTV Adjustments")}

      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-white/10 pt-5">
        <p className="text-xs text-gray-500">
          Changes are applied to the shared pricing matrix after saving.
        </p>
        <Button onClick={saveMatrix} disabled={saving}>
          {saving ? "Saving..." : "Save Matrix"}
        </Button>
      </div>
    </main>
  );
}
