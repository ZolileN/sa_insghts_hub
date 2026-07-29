"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const CHART_COLORS = [
  "#2563eb",
  "#059669",
  "#d97706",
  "#dc2626",
  "#7c3aed",
  "#0891b2",
  "#be185d",
  "#4f46e5",
];

export function SimpleBarChart({
  data,
  xKey,
  yKey,
  color = CHART_COLORS[0],
  layout = "vertical",
  height = 280,
  onCategoryClick,
  categoryFormatter,
}: {
  data: Record<string, unknown>[];
  xKey: string;
  yKey: string;
  color?: string;
  layout?: "vertical" | "horizontal";
  height?: number;
  onCategoryClick?: (label: string) => void;
  categoryFormatter?: (value: string) => string;
}) {
  const isVertical = layout === "vertical";
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={data}
        layout={isVertical ? "vertical" : "horizontal"}
        margin={{ top: 8, right: 16, left: isVertical ? 80 : 8, bottom: 8 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        {isVertical ? (
          <>
            <XAxis type="number" tick={{ fontSize: 11 }} stroke="var(--muted)" />
            <YAxis
              type="category"
              dataKey={xKey}
              tick={{ fontSize: 11 }}
              tickFormatter={categoryFormatter}
              stroke="var(--muted)"
              width={72}
            />
          </>
        ) : (
          <>
            <XAxis
              dataKey={xKey}
              tick={{ fontSize: 11 }}
              tickFormatter={categoryFormatter}
              stroke="var(--muted)"
            />
            <YAxis tick={{ fontSize: 11 }} stroke="var(--muted)" />
          </>
        )}
        <Tooltip
          contentStyle={{
            background: "var(--card)",
            border: "1px solid var(--border)",
            borderRadius: 8,
            fontSize: 12,
          }}
        />
        <Bar
          dataKey={yKey}
          fill={color}
          radius={[4, 4, 0, 0]}
          cursor={onCategoryClick ? "pointer" : undefined}
          onClick={
            onCategoryClick
              ? (bar) => {
                  const payload = bar?.payload as Record<string, unknown> | undefined;
                  const label = payload?.[xKey];
                  if (typeof label === "string") onCategoryClick(label);
                }
              : undefined
          }
        />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function MultiBarChart({
  data,
  xKey,
  keys,
  height = 280,
  onCategoryClick,
  categoryFormatter,
}: {
  data: Record<string, unknown>[];
  xKey: string;
  keys: { key: string; color: string; name?: string }[];
  height?: number;
  onCategoryClick?: (label: string) => void;
  categoryFormatter?: (value: string) => string;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 8, right: 16, left: 8, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis
          dataKey={xKey}
          tick={{ fontSize: 11 }}
          tickFormatter={categoryFormatter}
          stroke="var(--muted)"
        />
        <YAxis tick={{ fontSize: 11 }} stroke="var(--muted)" />
        <Tooltip
          contentStyle={{
            background: "var(--card)",
            border: "1px solid var(--border)",
            borderRadius: 8,
            fontSize: 12,
          }}
        />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        {keys.map((k) => (
          <Bar
            key={k.key}
            dataKey={k.key}
            name={k.name ?? k.key}
            fill={k.color}
            radius={[4, 4, 0, 0]}
            cursor={onCategoryClick ? "pointer" : undefined}
            onClick={
              onCategoryClick
                ? (bar) => {
                    const payload = bar?.payload as Record<string, unknown> | undefined;
                    const label = payload?.[xKey];
                    if (typeof label === "string") onCategoryClick(label);
                  }
                : undefined
            }
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}

export function SimpleLineChart({
  data,
  xKey,
  lines,
  height = 280,
}: {
  data: Record<string, unknown>[];
  xKey: string;
  lines: { key: string; color: string; name?: string }[];
  height?: number;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 8, right: 16, left: 8, bottom: 8 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis dataKey={xKey} tick={{ fontSize: 11 }} stroke="var(--muted)" />
        <YAxis tick={{ fontSize: 11 }} stroke="var(--muted)" />
        <Tooltip
          contentStyle={{
            background: "var(--card)",
            border: "1px solid var(--border)",
            borderRadius: 8,
            fontSize: 12,
          }}
        />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        {lines.map((l) => (
          <Line
            key={l.key}
            type="monotone"
            dataKey={l.key}
            name={l.name ?? l.key}
            stroke={l.color}
            strokeWidth={2}
            dot={false}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

export function SimplePieChart({
  data,
  nameKey,
  valueKey,
  height = 280,
}: {
  data: Record<string, unknown>[];
  nameKey: string;
  valueKey: string;
  height?: number;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={data}
          dataKey={valueKey}
          nameKey={nameKey}
          cx="50%"
          cy="50%"
          outerRadius={90}
          label={({ name, percent }) =>
            `${name} ${((percent ?? 0) * 100).toFixed(0)}%`
          }
          labelLine={false}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            background: "var(--card)",
            border: "1px solid var(--border)",
            borderRadius: 8,
            fontSize: 12,
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function ColoredBarChart({
  data,
  xKey,
  yKey,
  height = 280,
}: {
  data: { [key: string]: unknown; fill?: string }[];
  xKey: string;
  yKey: string;
  height?: number;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart
        data={data}
        layout="vertical"
        margin={{ top: 8, right: 24, left: 8, bottom: 8 }}
      >
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
        <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} />
        <YAxis
          type="category"
          dataKey={xKey}
          tick={{ fontSize: 11 }}
          width={100}
        />
        <Tooltip
          contentStyle={{
            background: "var(--card)",
            border: "1px solid var(--border)",
            borderRadius: 8,
            fontSize: 12,
          }}
        />
        <Bar dataKey={yKey} radius={[0, 4, 4, 0]}>
          {data.map((entry, i) => (
            <Cell
              key={i}
              fill={
                entry.fill ??
                (Number(entry[yKey]) >= 80
                  ? "#059669"
                  : Number(entry[yKey]) >= 60
                    ? "#2563eb"
                    : "#d97706")
              }
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
