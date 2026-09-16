const metrics = [
  ["Active Shipments", "128"],
  ["In Transit", "74"],
  ["Delivered Today", "42"],
  ["Fleet Utilisation", "86%"],
];

const shipments = [
  ["LF-10021", "Pretoria → Johannesburg", "In Transit"],
  ["LF-10022", "Cape Town → Durban", "Out for Delivery"],
  ["LF-10023", "Polokwane → Pretoria", "Delivered"],
];

export default function Dashboard() {
  return (
    <main className="shell">
      <aside className="sidebar">
        <div className="brand">LogiFlow<span>Enterprise</span></div>
        <nav>
          <a className="active">Dashboard</a>
          <a>Shipments</a>
          <a>Customers</a>
          <a>Drivers & Fleet</a>
          <a>Warehouses</a>
          <a>Invoices</a>
          <a>Analytics</a>
        </nav>
      </aside>

      <section className="content">
        <header className="topbar">
          <div><p className="eyebrow">OPERATIONS CONTROL CENTER</p><h1>Logistics Dashboard</h1></div>
          <button>+ Create Shipment</button>
        </header>

        <section className="metrics">
          {metrics.map(([label, value]) => <article className="metric" key={label}><span>{label}</span><strong>{value}</strong><small>Live operational metric</small></article>)}
        </section>

        <section className="grid">
          <article className="panel large">
            <div className="panel-head"><div><h2>Shipment Tracking</h2><p>Monitor active logistics operations.</p></div><button className="secondary">View all</button></div>
            <div className="table">
              <div className="row header"><span>ID</span><span>Route</span><span>Status</span></div>
              {shipments.map(([id, route, status]) => <div className="row" key={id}><strong>{id}</strong><span>{route}</span><span className={`status ${status.toLowerCase().replaceAll(" ", "-")}`}>{status}</span></div>)}
            </div>
          </article>

          <article className="panel">
            <h2>System Architecture</h2>
            <div className="architecture"><div>Next.js<br/><small>Web Client</small></div><i>↓</i><div>FastAPI<br/><small>REST API + JWT</small></div><i>↓</i><div>PostgreSQL<br/><small>Transactional Data</small></div></div>
          </article>
        </section>
      </section>
    </main>
  );
}
