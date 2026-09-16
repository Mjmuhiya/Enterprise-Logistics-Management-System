const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Shipment = {
  id: string;
  tracking_number: string;
  customer_id: string;
  origin: string;
  destination: string;
  weight_kg: number;
  status: string;
  created_at: string;
  updated_at: string;
};

export async function login(email: string, password: string) {
  const response = await fetch(`${API_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) throw new Error("Invalid email or password");
  return response.json() as Promise<{ access_token: string; token_type: string }>;
}

export async function getShipments(token: string) {
  const response = await fetch(`${API_URL}/api/v1/shipments`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });
  if (!response.ok) throw new Error("Unable to load shipments");
  return response.json() as Promise<Shipment[]>;
}
