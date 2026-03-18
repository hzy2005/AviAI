export async function getHealth() {
  const res = await fetch("/api/v1/health");
  if (!res.ok) {
    throw new Error(`Health check failed: ${res.status}`);
  }
  return res.json();
}
