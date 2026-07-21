import { getAllTopics, getAllMinistries } from "@/lib/mock-data";
import { FeedExplorer } from "@/components/FeedExplorer";
import { IntroAnimation } from "@/components/IntroAnimation";

export default function HomePage() {
  const topics = getAllTopics();
  const ministries = getAllMinistries();

  return (
    <>
      <IntroAnimation />
      <FeedExplorer topics={topics} ministries={ministries} />
    </>
  );
}
