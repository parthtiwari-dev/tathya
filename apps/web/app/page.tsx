import { getAllTopics } from "@/lib/mock-data";
import { FeedItem } from "@/components/FeedItem";
import { FilterSidebar } from "@/components/FilterSidebar";
import { IntroAnimation } from "@/components/IntroAnimation";

export default function HomePage() {
  const topics = getAllTopics();

  return (
    <>
      <IntroAnimation />
      <div className="flex gap-10 py-10">
        <FilterSidebar />
        <div className="min-w-0 flex-1">
          <h1 className="font-serif text-2xl font-medium text-ink">The Record</h1>
          <p className="mt-1 text-sm text-ink-secondary">
            Topics emerge automatically from configured sources. No topic on this feed was chosen by hand.
          </p>

          <div className="mt-8">
            {topics.map((topic) => (
              <FeedItem key={topic.id} topic={topic} />
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
