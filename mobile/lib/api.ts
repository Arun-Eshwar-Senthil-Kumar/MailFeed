// Android emulator: 10.0.2.2 | physical phone: your computer's LAN IP
export const API = "http://10.0.2.2:8000";

export type CalEvent = { title: string; start: string; end: string; url?: string | null; source_phrase: string };
export type Mail = { id: string; sender: string; subject: string; summary: string;
  priority: 1 | 2 | 3; urgency: number; timestamp: number; events: CalEvent[] };

export const getFeed = async (): Promise<{ stories: Mail[]; feed: Mail[] }> =>
  (await fetch(`${API}/feed`)).json();
export const archiveMail = (id: string) => fetch(`${API}/emails/${id}/archive`, { method: "POST" });
export const deleteMail = (id: string) => fetch(`${API}/emails/${id}`, { method: "DELETE" });
