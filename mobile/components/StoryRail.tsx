import { ScrollView, Text, TouchableOpacity, View } from "react-native";
import type { Mail } from "../lib/api";

export default function StoryRail({ stories, onOpen }: { stories: Mail[]; onOpen: (m: Mail) => void }) {
  if (!stories.length) return null;
  return (
    <View className="py-3 border-b border-black/5 bg-white">
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerClassName="px-4 gap-4">
        {stories.map((m) => (
          <TouchableOpacity key={m.id} onPress={() => onOpen(m)} className="items-center w-[72px]">
            <View className="w-[68px] h-[68px] rounded-full border-[3px] border-hot items-center justify-center">
              <View className="w-[56px] h-[56px] rounded-full bg-job items-center justify-center">
                <Text className="text-white text-xl font-bold">{(m.sender[0] ?? "?").toUpperCase()}</Text>
              </View>
            </View>
            <Text numberOfLines={1} className="text-[11px] text-ink mt-1">{m.sender}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );
}
