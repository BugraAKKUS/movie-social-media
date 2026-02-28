"use client";

interface VideoReviewCardProps {
  item: {
    id: string;
    author: { id: string; username: string; avatarUrl?: string };
    movie: { id: string; title: string; posterUrl?: string };
    contentText?: string;
    videoUrl?: string;
    rating?: number;
    watchedWith: { id: string; username: string }[];
    engagement: { likes: number; comments: number; views: number };
  };
}

export function VideoReviewCard({ item }: VideoReviewCardProps) {
  return (
    <div className="h-full w-full bg-black flex flex-col justify-end p-6 relative">
      {/* Video background */}
      {item.videoUrl && (
        <video
          src={item.videoUrl}
          className="absolute inset-0 w-full h-full object-cover"
          loop
          muted
          playsInline
        />
      )}

      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent" />

      {/* Content overlay */}
      <div className="relative z-10 space-y-3">
        {/* Author info */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gray-700 rounded-full" />
          <span className="font-semibold">@{item.author.username}</span>
        </div>

        {/* Movie + Rating */}
        <div className="flex items-center gap-2">
          <span className="text-lg font-bold">{item.movie.title}</span>
          {item.rating !== undefined && (
            <span className="px-2 py-0.5 bg-brand-600 rounded-full text-sm font-bold">
              {item.rating.toFixed(1)}/10
            </span>
          )}
        </div>

        {/* Review text */}
        {item.contentText && (
          <p className="text-sm text-gray-300 line-clamp-3">
            {item.contentText}
          </p>
        )}

        {/* Watched With tags */}
        {item.watchedWith.length > 0 && (
          <div className="flex items-center gap-1 text-sm text-gray-400">
            <span>Watched with</span>
            {item.watchedWith.map((u) => (
              <span key={u.id} className="text-brand-500">
                @{u.username}
              </span>
            ))}
          </div>
        )}

        {/* Engagement */}
        <div className="flex gap-4 text-sm text-gray-400">
          <span>{item.engagement.likes} likes</span>
          <span>{item.engagement.comments} comments</span>
        </div>
      </div>

      {/* Right-side action buttons */}
      <div className="absolute right-4 bottom-24 flex flex-col gap-6 items-center z-10">
        <button className="flex flex-col items-center gap-1">
          <HeartIcon />
          <span className="text-xs">{item.engagement.likes}</span>
        </button>
        <button className="flex flex-col items-center gap-1">
          <CommentIcon />
          <span className="text-xs">{item.engagement.comments}</span>
        </button>
        <button className="flex flex-col items-center gap-1">
          <ShareIcon />
          <span className="text-xs">Share</span>
        </button>
      </div>
    </div>
  );
}

function HeartIcon() {
  return (
    <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
    </svg>
  );
}

function CommentIcon() {
  return (
    <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
  );
}

function ShareIcon() {
  return (
    <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
        d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
    </svg>
  );
}
