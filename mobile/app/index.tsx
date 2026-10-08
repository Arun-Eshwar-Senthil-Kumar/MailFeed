import { useCallback, useEffect, useState } from "react";
import { ActivityIndicator, FlatList, Text, View, RefreshControl } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { archiveMail, deleteMail, getFeed, Mail } from "../lib/api";
import StoryRail from "../components/StoryRail";
import EmailCard from "../components/EmailCard";

export default function Feed() {
  const [feed, setFeed] = useState<Mail[]>([]);
  const [stories, setStories] = useState<Mail[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try { const d = await getFeed(); setFeed(d.feed); setStories(d.stories); setError(null); }
    catch { setError("Can't reach the server. Check that the backend is running."); }
    finally { setLoading(false); setRefreshing(false); }
  }, []);
  useEffect(() => { load(); }, [load]);

  const remove = (id: string, call: (id: string) => Promise<unknown>) => {
    const prevF = feed, prevS = stories;
    setFeed((f) => f.filter((m) => m.id !== id));       // optimistic
    setStories((s) => s.filter((m) => m.id !== id));
    call(id).catch(() => { setFeed(prevF); setStories(prevS); });
  };

  if (loading) return <View className="flex-1 items-center justify-center bg-paper"><ActivityIndicator /></View>;

  return (
    <SafeAreaView className="flex-1 bg-paper" edges={["top"]}>
      <View className="px-4 py-3 bg-white"><Text className="text-2xl font-extrabold text-ink">MailFeed</Text></View>
      <FlatList
        data={feed}
        keyExtractor={(m) => m.id}
        ListHeaderComponent={<>
          <StoryRail stories={stories} onOpen={() => {}} />
          <View className="h-3" />
        </>}
        renderItem={({ item }) => (
          <EmailCard mail={item}
            onArchive={() => remove(item.id, archiveMail)}
            onDelete={() => remove(item.id, deleteMail)} />
        )}
        ListEmptyComponent={<Text className="text-center text-black/50 mt-16 px-8">
          {error ?? "Nothing new. Pull down to refresh."}</Text>}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); load(); }} />}
      />
    </SafeAreaView>
  );
}
