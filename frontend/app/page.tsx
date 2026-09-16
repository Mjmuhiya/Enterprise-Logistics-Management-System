"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

import { getShipments, Shipment } from "../lib/api";

export default function Dashboard() {
  const router = useRouter();
  const [shipments, setShipments] = useState<Shipment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("logiflow_token");
    if (!token) {
      router.replace("/login");
      return;
    }
    getShipments(token)
      .then(setShipments)
      .catch(() => {
        localStorage.removeItem("logiflow_token");
        setError("Session expired. Please sign in again.");
        router.replace("/login");
      })
      .finally(() => setLoading(false));
  }, [router]);

  const active = shipments.filter((s) => !["DELIVERED", "CANCELLED"].includes(s.status)).length;
  const inTransit = shipments.filter((s) => ["IN_TRANSIT", "OUT_FOR_DELIVERY"].includes(s.status)).length;
  const delivered = shipments.filter((s) => s.status === "DELIVERED").length;
  const metrics = [
    ["Active Shipments", String(active)],
    ["In Transit", String(inTransit)],
    ["Delivered", String(delivered)],
    ["Total Shipments", String(shipments.length)],
  ];

  const visibleShipments = useMemo(() => shipments.slice(0, 8), [shipments]);

  function logout() {
    localStorage.removeItem("logiflow_token");
    router.push("/login");
  }

  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand">LogiFlow<span>Enterprise</span></div>
        <nav><a className="active">Dashboard</a><a>Shipments</a><a>Customers</a><a>Drivers & Fleet</a><a>Warehouses</a><a>Invoices</a><a>Analytics</a></nav>
        <button className="logout" onClick={logout}>Sign out</button>
      </aside>
      <section className="content">
        <header className="topbar">
          <div><p className="eyebrow">OPERATIONS CONTROL CENTER</p><h1>Logistics Dashboard</h1></div>
          <button>+ Create Shipment</button>
        </header>
        {error && <div className="error">{error}</div>}
        <section className="metrics">{metrics.map(([label, value]) => <article className="metric" key={label}><span>{label}</span><strong>{value}</strong><small>Live API metric</small></article>)}</section>
        <section className="grid">
          <article className="panel large">
            <div className="panel-head"><div><h2>Shipment Tracking</h2><p>Live data from FastAPI and PostgreSQL.</p></div><button className="secondary">View all</button></div>
            {loading ? <p>Loading shipments…</p> : visibleShipments.length === 0 ? <p>No shipments available.</p> : <div className="table"><div className="row header"><span>Tracking</span><span>Route</span><span>Status</span></div>{visibleShipments.map((shipment) => <div className="row" key={shipment.id}><strong>{shipment.tracking_number}</strong><span>{shipment.origin} → {shipment.destination}</span><span className={`status ${shipment.status.toLowerCase().replaceAll("_", "-")}`}>{shipment.status.replaceAll("_", " ")}</span></div>)}</div>}
          </article>
          <article className="panel"><h2>System Architecture</h2><div className="architecture"><div>Next.js<br/><small>Web Client</small></div><i>↓</i><div>FastAPI<br/><small>REST API + JWT</small></div><i>↓</i><div>PostgreSQL<br/><small>Transactional Data</small></div></div></article>
        </section>
      </section>
    </main>
  );
}
