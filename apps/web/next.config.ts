import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@cinesocial/ui", "@cinesocial/shared"],
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "image.tmdb.org",
      },
    ],
  },
};

export default nextConfig;
