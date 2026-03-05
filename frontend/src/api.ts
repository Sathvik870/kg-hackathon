const API_URL = "http://localhost:8000";

export const connectToDb = async (details: any) => {
  const res = await fetch(`${API_URL}/api/connect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(details)
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
};

export const getStructure = async () => {
  const res = await fetch(`${API_URL}/api/structure`);
  return res.json();
};

export const previewTable = async (db: string, table: string) => {
  const res = await fetch(`${API_URL}/api/preview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ db, table })
  });
  return res.json();
};