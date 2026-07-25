import type { MetadataRoute } from "next";
import { getAllTopics, getAllMinistries, getAllSources } from "@/lib/api";

const SITE_URL = "https://tathya-1.vercel.app";

// Dynamic sitemap: rebuilt on every request to Google (Next revalidates this
// route like any other), so newly persisted topics get discovered without a
// redeploy. If the API is briefly unreachable, fall back to the static
// routes only rather than failing the whole sitemap.
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const staticRoutes: MetadataRoute.Sitemap = [
    { url: SITE_URL, changeFrequency: "hourly", priority: 1 },
    { url: `${SITE_URL}/sources`, changeFrequency: "daily", priority: 0.6 },
    { url: `${SITE_URL}/search`, changeFrequency: "monthly", priority: 0.3 },
    { url: `${SITE_URL}/about`, changeFrequency: "monthly", priority: 0.3 },
  ];

  try {
    const [topics, ministries, sources] = await Promise.all([
      getAllTopics(),
      getAllMinistries(),
      getAllSources(),
    ]);

    const topicRoutes: MetadataRoute.Sitemap = topics.map((topic) => ({
      url: `${SITE_URL}/topic/${topic.slug}`,
      lastModified: topic.lastSignalAt,
      changeFrequency: topic.status === "live" ? "daily" : "weekly",
      priority: topic.status === "live" ? 0.9 : 0.5,
    }));

    const ministryRoutes: MetadataRoute.Sitemap = ministries.map((ministry) => ({
      url: `${SITE_URL}/ministry/${ministry.slug}`,
      changeFrequency: "daily",
      priority: 0.6,
    }));

    const sourceRoutes: MetadataRoute.Sitemap = sources.map((source) => ({
      url: `${SITE_URL}/source/${source.sourceKey}`,
      changeFrequency: "weekly",
      priority: 0.4,
    }));

    return [...staticRoutes, ...topicRoutes, ...ministryRoutes, ...sourceRoutes];
  } catch {
    return staticRoutes;
  }
}
