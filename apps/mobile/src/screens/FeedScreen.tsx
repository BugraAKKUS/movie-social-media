import React, { useState, useCallback } from "react";
import {
  View,
  Text,
  FlatList,
  Dimensions,
  StyleSheet,
  TouchableOpacity,
} from "react-native";

const { height: SCREEN_HEIGHT } = Dimensions.get("window");

interface FeedItem {
  id: string;
  author: { username: string };
  movie: { title: string };
  contentText?: string;
  rating?: number;
  spoiler: { isSpoiler: boolean };
}

export default function FeedScreen() {
  const [items, setItems] = useState<FeedItem[]>([]);

  const renderItem = useCallback(
    ({ item }: { item: FeedItem }) => (
      <View style={styles.feedItem}>
        <View style={styles.overlay}>
          <Text style={styles.username}>@{item.author.username}</Text>
          <View style={styles.movieRow}>
            <Text style={styles.movieTitle}>{item.movie.title}</Text>
            {item.rating !== undefined && (
              <View style={styles.ratingBadge}>
                <Text style={styles.ratingText}>
                  {item.rating.toFixed(1)}/10
                </Text>
              </View>
            )}
          </View>
          {item.contentText && (
            <Text style={styles.reviewText} numberOfLines={3}>
              {item.contentText}
            </Text>
          )}
        </View>

        {/* Spoiler overlay */}
        {item.spoiler.isSpoiler && (
          <View style={styles.spoilerOverlay}>
            <Text style={styles.spoilerIcon}>&#9888;</Text>
            <Text style={styles.spoilerTitle}>Spoiler Warning</Text>
            <TouchableOpacity style={styles.revealButton}>
              <Text style={styles.revealText}>Tap to Reveal</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>
    ),
    [],
  );

  return (
    <FlatList
      data={items}
      renderItem={renderItem}
      keyExtractor={(item) => item.id}
      pagingEnabled
      showsVerticalScrollIndicator={false}
      snapToInterval={SCREEN_HEIGHT}
      decelerationRate="fast"
      ListEmptyComponent={
        <View style={[styles.feedItem, styles.emptyState]}>
          <Text style={styles.emptyTitle}>Your feed is empty</Text>
          <Text style={styles.emptySubtitle}>
            Follow users and rate movies to get started
          </Text>
        </View>
      }
    />
  );
}

const styles = StyleSheet.create({
  feedItem: {
    height: SCREEN_HEIGHT,
    backgroundColor: "#000",
    justifyContent: "flex-end",
  },
  overlay: {
    padding: 24,
    paddingBottom: 80,
  },
  username: {
    color: "#fff",
    fontWeight: "600",
    fontSize: 16,
    marginBottom: 8,
  },
  movieRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 8,
  },
  movieTitle: {
    color: "#fff",
    fontWeight: "700",
    fontSize: 18,
  },
  ratingBadge: {
    backgroundColor: "#dc2626",
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 12,
  },
  ratingText: {
    color: "#fff",
    fontWeight: "700",
    fontSize: 12,
  },
  reviewText: {
    color: "#d1d5db",
    fontSize: 14,
    lineHeight: 20,
  },
  spoilerOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "rgba(0,0,0,0.85)",
    justifyContent: "center",
    alignItems: "center",
  },
  spoilerIcon: {
    fontSize: 48,
    marginBottom: 12,
  },
  spoilerTitle: {
    color: "#fff",
    fontSize: 20,
    fontWeight: "700",
    marginBottom: 16,
  },
  revealButton: {
    borderWidth: 1,
    borderColor: "#4b5563",
    paddingHorizontal: 24,
    paddingVertical: 10,
    borderRadius: 24,
  },
  revealText: {
    color: "#fff",
    fontSize: 14,
  },
  emptyState: {
    justifyContent: "center",
    alignItems: "center",
  },
  emptyTitle: {
    color: "#fff",
    fontSize: 20,
    marginBottom: 8,
  },
  emptySubtitle: {
    color: "#9ca3af",
    fontSize: 14,
  },
});
