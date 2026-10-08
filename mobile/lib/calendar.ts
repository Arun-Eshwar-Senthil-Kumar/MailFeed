import * as Calendar from "expo-calendar";
import { Platform } from "react-native";
import type { CalEvent } from "./api";

async function writableCalendarId(): Promise<string> {
  const cals = await Calendar.getCalendarsAsync(Calendar.EntityTypes.EVENT);
  const writable = cals.find((c) => c.allowsModifications &&
    (Platform.OS === "ios" ? c.source.name === "iCloud" || c.isPrimary : c.isPrimary)) ??
    cals.find((c) => c.allowsModifications);
  if (writable) return writable.id;
  return Calendar.createCalendarAsync({ title: "MailFeed", color: "#FF4D2E",
    entityType: Calendar.EntityTypes.EVENT, name: "mailfeed",
    source: { isLocalAccount: true, name: "MailFeed", type: Calendar.SourceType.LOCAL },
    ownerAccount: "personal", accessLevel: Calendar.CalendarAccessLevel.OWNER });
}

/** Pushes one parsed event to the device calendar. Returns false if permission denied. */
export async function addToCalendar(ev: CalEvent): Promise<boolean> {
  const { status } = await Calendar.requestCalendarPermissionsAsync();
  if (status !== "granted") return false;
  await Calendar.createEventAsync(await writableCalendarId(), {
    title: ev.title, startDate: new Date(ev.start), endDate: new Date(ev.end),
    notes: ev.url ? `Registration / details: ${ev.url}` : undefined,
    url: ev.url ?? undefined,                       // iOS only
    alarms: [{ relativeOffset: -60 }, { relativeOffset: -24 * 60 }],
  });
  return true;
}
