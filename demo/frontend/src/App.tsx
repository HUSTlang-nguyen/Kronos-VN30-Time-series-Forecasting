import { useEffect, useMemo, useState } from "react";
import {
  ArrowDownToLine,
  ArrowUpRight,
  ChartNoAxesCombined,
  Check,
  ChevronRight,
  CircleHelp,
  Cpu,
  Globe2,
  Layers3,
  Loader2,
  Moon,
  SlidersHorizontal,
  Sun,
  Terminal,
  TrendingUp,
} from "lucide-react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceArea,
  ReferenceLine,
  XAxis,
  YAxis,
} from "recharts";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { Skeleton } from "@/components/ui/skeleton";
import { vi, en, type Language } from "./i18n";

type Candle = {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  step?: number;
};
type Model = {
  id: string;
  label: string;
  variant: "mini" | "small" | "base";
  parameters: number;
};
type Catalog = {
  models: Model[];
  origins: string[];
  default_origin: string;
  default_model: string;
  snapshot_end: string;
};
type Result = {
  predictions: Candle[];
  elapsed_seconds: number;
  device: string;
  device_name: string;
  fallback_reason: string | null;
};
type Job = {
  id: string;
  model_id: string;
  origin: string;
  status: string;
  result?: Result;
  error?: string;
};
type History = { history: Candle[]; future_dates: string[] };

async function api<T>(path: string, body?: unknown): Promise<T> {
  let response: Response;
  try {
    response = await fetch(
      path,
      body
        ? {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
          }
        : undefined,
    );
  } catch {
    throw new Error("NETWORK");
  }
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.error || "INFERENCE_FAILED");
  }
  return response.json();
}
function stored(key: string, fallback: string) {
  try {
    return localStorage.getItem(key) || fallback;
  } catch {
    return fallback;
  }
}

export default function App() {
  const [language, setLanguage] = useState<Language>(() =>
    stored("vn30-language", "vi") === "en" ? "en" : "vi",
  );
  const [dark, setDark] = useState(
    () => stored("vn30-theme", "dark") !== "light",
  );
  const t = language === "vi" ? vi : en;
  const locale = language === "vi" ? "vi-VN" : "en-US";
  const number = (n: number, digits = 2) =>
    new Intl.NumberFormat(locale, {
      minimumFractionDigits: digits,
      maximumFractionDigits: digits,
    }).format(n);
  const date = (value: string, short = false) =>
    new Intl.DateTimeFormat(locale, {
      day: "2-digit",
      month: "2-digit",
      ...(short ? {} : { year: "numeric" }),
      timeZone: "UTC",
    }).format(new Date(value + "T00:00:00Z"));
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [model, setModel] = useState("kronos-small");
  const [origin, setOrigin] = useState("");
  const [history, setHistory] = useState<History | null>(null);
  const [target, setTarget] = useState<"open" | "close">("close");
  const [horizon, setHorizon] = useState(20);
  const [showActual, setShowActual] = useState(false);
  const [actual, setActual] = useState<Candle[]>([]);
  const [job, setJob] = useState<Job | null>(null);
  const [error, setError] = useState("");
  const [device, setDevice] = useState("");
  const [reconnect, setReconnect] = useState(0);
  const busy = Boolean(
    job && ["queued", "loading", "running"].includes(job.status),
  );
  const result = job?.status === "complete" ? job.result : undefined;

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    try {
      localStorage.setItem("vn30-theme", dark ? "dark" : "light");
    } catch {}
  }, [dark]);
  useEffect(() => {
    document.documentElement.lang = language;
    try {
      localStorage.setItem("vn30-language", language);
    } catch {}
  }, [language]);
  useEffect(() => {
    let live = true;
    api<Catalog>("/api/catalog")
      .then((data) => {
        if (live) {
          setCatalog(data);
          setOrigin(data.default_origin);
          setModel(data.default_model);
          setError("");
        }
      })
      .catch((e) => live && setError(e.message));
    api<{ device_name: string }>("/api/health")
      .then((d) => live && setDevice(d.device_name))
      .catch(() => {});
    return () => {
      live = false;
    };
  }, [reconnect]);
  useEffect(() => {
    if (!origin) return;
    let live = true;
    setHistory(null);
    setJob(null);
    setActual([]);
    setShowActual(false);
    api<History>("/api/history/" + origin)
      .then((data) => live && setHistory(data))
      .catch((e) => live && setError(e.message));
    return () => {
      live = false;
    };
  }, [origin]);
  useEffect(() => {
    if (!busy || !job?.id) return;
    let live = true;
    const timer = setTimeout(() => {
      api<Job>("/api/jobs/" + job.id)
        .then((data) => {
          if (live) {
            setJob(data);
            if (data.error) setError(data.error);
          }
        })
        .catch((e) => {
          if (live) {
            setError(e.message);
            setJob({ ...job, status: "error" });
          }
        });
    }, 750);
    return () => {
      live = false;
      clearTimeout(timer);
    };
  }, [job, busy]);
  useEffect(() => {
    if (!showActual || !origin) return;
    let live = true;
    api<{ actual: Candle[] }>("/api/reference/" + origin)
      .then((d) => live && setActual(d.actual))
      .catch((e) => live && setError(e.message));
    return () => {
      live = false;
    };
  }, [showActual, origin]);

  const points = useMemo(() => {
    if (!history) return [];
    const past = history.history
      .slice(-64)
      .map((row) => ({
        date: row.date,
        history: row[target],
        forecast: null as number | null,
        actual: null as number | null,
      }));
    const future = history.future_dates
      .slice(0, horizon)
      .map((day, i) => ({
        date: day,
        history: null as number | null,
        forecast: result?.predictions[i]?.[target] ?? null,
        actual: showActual ? (actual[i]?.[target] ?? null) : null,
      }));
    return [...past, ...future];
  }, [history, target, horizon, result, actual, showActual]);
  const lastClose = history?.history.at(-1)?.close ?? 0;
  const activeModel = catalog?.models.find((m) => m.id === model);
  const status = busy
    ? t[job!.status as "queued" | "loading" | "running"]
    : result
      ? t.complete
      : t.notRun;
  async function run() {
    setError("");
    setJob({ id: "", model_id: model, origin, status: "queued" });
    try {
      setJob(await api<Job>("/api/forecasts", { model_id: model, origin }));
    } catch (e) {
      setJob(null);
      setError((e as Error).message);
    }
  }

  return (
    <TooltipProvider>
      <div className="studio-shell">
        <header className="topbar">
          <div className="brand">
            <span className="brand-symbol">
              <ChartNoAxesCombined size={21} />
            </span>
            <span>
              VN30<span className="brand-slash">/</span>STUDIO
            </span>
          </div>
          <div className="header-actions">
            <span className="local-label">
              <span className="status-dot" />
              {t.local}
            </span>
            <div className="header-divider" />
            <Button
              variant="ghost"
              size="sm"
              aria-label={t.langSwitch}
              onClick={() => setLanguage(language === "vi" ? "en" : "vi")}
            >
              <Globe2 size={14} />
              <span
                className={language === "vi" ? "" : "text-muted-foreground"}
              >
                VI
              </span>
              <span className="text-muted-foreground">/</span>
              <span
                className={language === "en" ? "" : "text-muted-foreground"}
              >
                EN
              </span>
            </Button>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label={dark ? t.switchLight : t.switchDark}
                  onClick={() => setDark(!dark)}
                >
                  {dark ? <Sun size={17} /> : <Moon size={17} />}
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                {dark ? t.switchLight : t.switchDark}
              </TooltipContent>
            </Tooltip>
          </div>
        </header>
        <main className="studio-main">
          <section className="intro">
            <div>
              <div className="eyebrow">
                <span className="tiny-line" /> KRONOS · VN30
              </div>
              <h1>{t.title}</h1>
              <p>{t.intro}</p>
            </div>
            <div className="intro-badge">
              <Badge variant="secondary">{t.experimental}</Badge>
              <Badge variant="outline">{t.historical}</Badge>
              <span>
                {t.snapshot} {catalog ? date(catalog.snapshot_end) : "—"}
              </span>
            </div>
          </section>
          {error && (
            <Alert variant="destructive" className="error-banner">
              <CircleHelp />
              <AlertTitle>{t.errorTitle}</AlertTitle>
              <AlertDescription>
                {t[error as keyof typeof t] || t.INFERENCE_FAILED}
                {!catalog && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setReconnect(reconnect + 1)}
                  >
                    {t.retry}
                  </Button>
                )}
              </AlertDescription>
            </Alert>
          )}
          <div className="workspace">
            <aside>
              <Card className="setup-card">
                <div className="section-header">
                  <SlidersHorizontal size={15} />
                  <h2>{t.setup}</h2>
                  <span className="section-number">01</span>
                </div>
                <CardContent className="setup-content">
                  <label className="field-label">{t.model}</label>
                  <div className="model-options">
                    {catalog
                      ? catalog.models.map((item, index) => (
                          <button
                            key={item.id}
                            disabled={busy}
                            className={
                              "model-option " +
                              (model === item.id ? "selected" : "")
                            }
                            aria-pressed={model === item.id}
                            onClick={() => {
                              setModel(item.id);
                              setJob(null);
                              setError("");
                            }}
                          >
                            <span className="model-icon">
                              <Layers3
                                size={18}
                                strokeWidth={
                                  index === 0 ? 1.2 : index === 1 ? 1.6 : 2
                                }
                              />
                            </span>
                            <span className="model-copy">
                              <strong>{item.label}</strong>
                              <small>
                                {t[item.variant]} <span>·</span>{" "}
                                {(item.parameters / 1e6).toFixed(1)}M
                              </small>
                            </span>
                            {model === item.id ? (
                              <Check size={15} />
                            ) : (
                              <span className="empty-check" />
                            )}
                          </button>
                        ))
                      : [0, 1, 2].map((i) => (
                          <Skeleton key={i} className="h-17 w-full" />
                        ))}
                  </div>
                  <div className="control-rule" />
                  <div className="field-label-row">
                    <label className="field-label" id="origin-label">
                      {t.origin}
                    </label>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <button
                          aria-label={t.originHint}
                          className="help-button"
                        >
                          <CircleHelp size={13} />
                        </button>
                      </TooltipTrigger>
                      <TooltipContent side="right">
                        {t.originHint}
                      </TooltipContent>
                    </Tooltip>
                  </div>
                  <Select
                    value={origin}
                    disabled={!catalog || busy}
                    onValueChange={(value) => {
                      setOrigin(value);
                      setError("");
                    }}
                  >
                    <SelectTrigger
                      aria-labelledby="origin-label"
                      className="w-full h-10! font-mono"
                    >
                      <SelectValue placeholder="—" />
                    </SelectTrigger>
                    <SelectContent>
                      {catalog?.origins.toReversed().map((day) => (
                        <SelectItem key={day} value={day}>
                          {date(day)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <div className="context-grid">
                    <div>
                      <span>128</span>
                      <small>{t.context}</small>
                    </div>
                    <div>
                      <span>20</span>
                      <small>{t.future}</small>
                    </div>
                  </div>
                  <Button
                    className="run-button w-full h-11!"
                    disabled={!history || busy}
                    onClick={run}
                  >
                    {busy ? (
                      <Loader2 className="animate-spin" />
                    ) : (
                      <TrendingUp size={16} />
                    )}
                    <span>{busy ? status : result ? t.rerun : t.run}</span>
                    {!busy && <ArrowUpRight className="ml-auto" size={16} />}
                  </Button>
                  <p className="setup-foot">
                    <Terminal size={12} />
                    {t.localNote}
                  </p>
                </CardContent>
              </Card>
              <div className="aside-note">
                <Badge variant="secondary">{t.experimental}</Badge>
                <p>{t.note}</p>
              </div>
            </aside>
            <section className="forecast-space">
              <Card className="chart-card">
                <div className="chart-toolbar">
                  <div>
                    <span className="eyebrow small">VN30 INDEX</span>
                    <h2>{t.priceChart}</h2>
                  </div>
                  <Tabs
                    value={target}
                    onValueChange={(value) =>
                      setTarget(value as "open" | "close")
                    }
                  >
                    <TabsList>
                      <TabsTrigger value="close">{t.close}</TabsTrigger>
                      <TabsTrigger value="open">{t.open}</TabsTrigger>
                    </TabsList>
                  </Tabs>
                </div>
                <div className="chart-meta">
                  <div className="legend">
                    <span>
                      <i className="history-line" />
                      {t.history}
                    </span>
                    <span>
                      <i className="forecast-line" />
                      {t.forecast}
                    </span>
                    {showActual && (
                      <span>
                        <i className="actual-line" />
                        {t.actual}
                      </span>
                    )}
                  </div>
                  <div className="horizon-control">
                    <span>{t.sessions}</span>
                    {[1, 5, 20].map((h) => (
                      <Button
                        key={h}
                        variant={horizon === h ? "secondary" : "ghost"}
                        size="xs"
                        aria-pressed={horizon === h}
                        aria-label={`${h} ${t.sessions.toLowerCase()}`}
                        onClick={() => setHorizon(h)}
                      >
                        {h}
                      </Button>
                    ))}
                  </div>
                </div>
                <div className="chart-area">
                  {history ? (
                    <ChartContainer
                      config={{
                        history: {
                          label: t.history,
                          color: "var(--muted-foreground)",
                        },
                        forecast: {
                          label: t.forecast,
                          color: "var(--foreground)",
                        },
                        actual: { label: t.actual, color: "var(--chart-2)" },
                      }}
                      className="h-full w-full aspect-auto"
                    >
                      <LineChart
                        accessibilityLayer
                        data={points}
                        margin={{ top: 25, right: 22, left: 0, bottom: 8 }}
                      >
                        <CartesianGrid
                          vertical={false}
                          strokeDasharray="3 5"
                          strokeOpacity={0.55}
                        />
                        <XAxis
                          dataKey="date"
                          axisLine={false}
                          tickLine={false}
                          minTickGap={36}
                          tickMargin={12}
                          tickFormatter={(d) => date(d, true)}
                        />
                        <YAxis
                          width={66}
                          axisLine={false}
                          tickLine={false}
                          tickFormatter={(v) => number(v, 0)}
                          domain={[
                            (min: number) => Math.floor((min - 15) / 10) * 10,
                            (max: number) => Math.ceil((max + 15) / 10) * 10,
                          ]}
                          tickMargin={10}
                        />
                        <ReferenceArea
                          x1={origin}
                          x2={history.future_dates[horizon - 1]}
                          fill="var(--foreground)"
                          fillOpacity={0.025}
                        />
                        <ReferenceLine
                          x={origin}
                          stroke="var(--muted-foreground)"
                          strokeDasharray="3 5"
                          label={{
                            value: t.originLabel,
                            position: "insideTopRight",
                            fill: "var(--muted-foreground)",
                            fontSize: 9,
                          }}
                        />
                        <ChartTooltip
                          content={
                            <ChartTooltipContent
                              labelFormatter={(d) => date(String(d))}
                              formatter={(value, name) => (
                                <div className="flex min-w-32 justify-between gap-5 text-xs">
                                  <span className="text-muted-foreground">
                                    {
                                      t[
                                        name as
                                          "history" | "forecast" | "actual"
                                      ]
                                    }
                                  </span>
                                  <strong className="font-mono">
                                    {number(Number(value))}
                                  </strong>
                                </div>
                              )}
                            />
                          }
                        />
                        <Line
                          name="history"
                          dataKey="history"
                          type="linear"
                          stroke="var(--muted-foreground)"
                          strokeWidth={1.7}
                          dot={false}
                          isAnimationActive={false}
                        />
                        <Line
                          name="forecast"
                          dataKey="forecast"
                          type="linear"
                          stroke="var(--foreground)"
                          strokeWidth={2}
                          strokeDasharray="5 4"
                          dot={{
                            r: 2,
                            fill: "var(--foreground)",
                            strokeWidth: 0,
                          }}
                          isAnimationActive={false}
                        />
                        {showActual && (
                          <Line
                            name="actual"
                            dataKey="actual"
                            type="linear"
                            stroke="var(--chart-2)"
                            strokeWidth={1.5}
                            dot={false}
                            isAnimationActive={false}
                          />
                        )}
                      </LineChart>
                    </ChartContainer>
                  ) : (
                    <div className="chart-loading">
                      <Skeleton className="h-2/3 w-11/12" />
                    </div>
                  )}
                  {history && !result && horizon === 20 && (
                    <div className="forecast-placeholder">
                      <ChartNoAxesCombined size={21} strokeWidth={1} />
                      <span>{busy ? status : t.waitingTitle}</span>
                      <small>
                        {busy ? (
                          <Loader2 size={14} className="animate-spin" />
                        ) : (
                          t.waiting
                        )}
                      </small>
                    </div>
                  )}
                </div>
                <div className="chart-bottom">
                  <span className={"run-status " + (busy ? "busy" : "")}>
                    <span className="status-dot" />
                    {status}
                  </span>
                  <label className="actual-switch">
                    <Switch
                      checked={showActual}
                      onCheckedChange={setShowActual}
                      aria-label={t.showActual}
                    />
                    {t.showActual}
                  </label>
                </div>
              </Card>
              <div className="forecast-stats">
                {[1, 5, 20].map((h, i) => {
                  const value = result?.predictions[h - 1]?.[target];
                  const change =
                    value !== undefined && lastClose
                      ? (value / lastClose - 1) * 100
                      : null;
                  return (
                    <Card key={h} className="stat-card">
                      <CardContent>
                        <div className="stat-top">
                          <span>{[t.next, t.after5, t.after20][i]}</span>
                          <span className="font-mono text-muted-foreground">
                            h={h}
                          </span>
                        </div>
                        <div className="stat-value">
                          {value !== undefined ? (
                            number(value)
                          ) : busy ? (
                            <Skeleton className="h-8 w-28" />
                          ) : (
                            "—"
                          )}
                          <small>{t.points}</small>
                        </div>
                        <div className="stat-change">
                          {change !== null ? (
                            <>
                              <span>
                                {change >= 0 ? "+" : ""}
                                {number(change)}%
                              </span>
                              <small>{t.vsOrigin}</small>
                            </>
                          ) : (
                            <span className="text-muted-foreground">
                              {t.waiting}
                            </span>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </section>
          </div>
          <Card className="results-card">
            <div className="results-header">
              <div>
                <div className="section-heading">
                  <h2>{t.results}</h2>
                  {result && <Badge variant="secondary">20</Badge>}
                </div>
                <p>{t.resultsHint}</p>
              </div>
              <Button
                variant="outline"
                disabled={!result}
                onClick={() => {
                  window.location.href =
                    "/api/jobs/" + job!.id + "/forecast.csv";
                }}
              >
                <ArrowDownToLine size={14} />
                {t.export}
              </Button>
            </div>
            {result ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{t.session}</TableHead>
                    <TableHead>{t.date}</TableHead>
                    <TableHead className="text-right">{t.open}</TableHead>
                    <TableHead className="text-right">{t.close}</TableHead>
                    {showActual && (
                      <TableHead className="text-right">
                        {t.actual} · {t[target]}
                      </TableHead>
                    )}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {result.predictions.map((row, i) => (
                    <TableRow key={row.date}>
                      <TableCell className="font-mono">
                        <span
                          className={
                            [1, 5, 20].includes(i + 1) ? "key-session" : ""
                          }
                        >
                          +{String(i + 1).padStart(2, "0")}
                        </span>
                      </TableCell>
                      <TableCell>{date(row.date)}</TableCell>
                      <TableCell className="text-right font-mono">
                        {number(row.open)}
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        {number(row.close)}
                      </TableCell>
                      {showActual && (
                        <TableCell className="text-right font-mono text-muted-foreground">
                          {actual[i] ? number(actual[i][target]) : "—"}
                        </TableCell>
                      )}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="empty-results">
                <ChartNoAxesCombined size={24} strokeWidth={1} />
                <p>{t.noResults}</p>
                <span className="text-muted-foreground">
                  <ChevronRight size={12} />
                  {t.protocol}
                </span>
              </div>
            )}
          </Card>
          <footer>
            <span>
              {t.builtWith}
              <span className="footer-dot">·</span>
              {t.historical}
            </span>
            <div>
              <Cpu size={13} />
              <span>
                {result?.device_name.replace("NVIDIA GeForce ", "") ||
                  device.replace("NVIDIA GeForce ", "") ||
                  t.localSession}
              </span>
              {result && (
                <>
                  <span className="footer-dot">·</span>
                  <span>
                    {number(result.elapsed_seconds, 1)} {t.seconds}
                  </span>
                </>
              )}
            </div>
          </footer>
          {result?.fallback_reason && (
            <p className="fallback-note">{t.cpuFallback}</p>
          )}
          <span className="sr-only" aria-live="polite">
            {busy ? status : result ? t.complete : ""}
          </span>
          <span className="sr-only">{activeModel?.label}</span>
        </main>
      </div>
    </TooltipProvider>
  );
}
