import { Alert, Linking, Text, TouchableOpacity, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import type { Mail } from "../lib/api";
import { addToCalendar } from "../lib/calendar";

const TIER = {
  1: { label: "Job / Internship", bar: "bg-job", chip: "bg-job/10 text-job" },
  2: { label: "Deadline", bar: "bg-due", chip: "bg-due/15 text-[#9A6200]" },
  3: { label: "General", bar: "bg-black/20", chip: "bg-black/5 text-black/60" },
} as const;

type Props = { mail: Mail; onArchive: () => void; onDelete: () => void };

export default function EmailCard({ mail, onArchive, onDelete }: Props) {
  const t = TIER[mail.priority];
  const ev = mail.events[0];

  const calendar = async () => {
    if (!ev) return Alert.alert("No date found", "This email has no upcoming date or time.");
    const ok = await addToCalendar(ev);
    Alert.alert(ok ? "Added to calendar" : "Calendar access needed",
      ok ? new Date(ev.start).toLocaleString() : "Allow calendar access in Settings.");
  };

  const Action = ({ icon, label, onPress, active }: any) => (
    <TouchableOpacity onPress={onPress} className="flex-row items-center gap-1.5 py-1 pr-5">
      <Ionicons name={icon} size={24} color={active ? "#FF4D2E" : "#14181F"} />
      <Text className="text-xs text-ink">{label}</Text>
    </TouchableOpacity>
  );

  return (
    <View className="bg-white mx-3 mb-3 rounded-2xl overflow-hidden border border-black/5">
      <View className={`h-1 ${t.bar}`} />
      <View className="p-4">
        <View className="flex-row items-center justify-between mb-2">
          <View className="flex-row items-center gap-2 flex-1">
            <View className="w-9 h-9 rounded-full bg-ink items-center justify-center">
              <Text className="text-white font-bold">{(mail.sender[0] ?? "?").toUpperCase()}</Text>
            </View>
            <Text numberOfLines={1} className="font-semibold text-ink flex-1">{mail.sender}</Text>
          </View>
          <Text className={`text-[11px] px-2 py-1 rounded-full overflow-hidden ${t.chip}`}>{t.label}</Text>
        </View>

        <Text className="text-[17px] font-bold text-ink leading-6">{mail.subject}</Text>
        <Text className="text-[15px] text-black/70 leading-[22px] mt-1">{mail.summary}</Text>

        {ev && (
          <View className="flex-row items-center gap-2 mt-3 bg-paper rounded-xl p-3">
            <Ionicons name="time-outline" size={18} color="#14181F" />
            <Text className="flex-1 text-[13px] text-ink">
              {new Date(ev.start).toLocaleString([], { weekday: "short", day: "numeric", month: "short", hour: "numeric", minute: "2-digit" })}
            </Text>
            {ev.url && (
              <TouchableOpacity onPress={() => Linking.openURL(ev.url!)}>
                <Text className="text-job font-semibold text-[13px]">Register</Text>
              </TouchableOpacity>
            )}
          </View>
        )}

        <View className="flex-row mt-3 pt-2 border-t border-black/5">
          <Action icon="calendar-outline" label="Add" onPress={calendar} active={!!ev} />
          <Action icon="archive-outline" label="Archive" onPress={onArchive} />
          <Action icon="trash-outline" label="Delete" onPress={onDelete} />
        </View>
      </View>
    </View>
  );
}
