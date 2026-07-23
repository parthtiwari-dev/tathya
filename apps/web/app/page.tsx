import { getAllTopics, getAllMinistries } from "@/lib/api";
import { FeedExplorer } from "@/components/FeedExplorer";
import { IntroAnimation } from "@/components/IntroAnimation";

export default async function HomePage() {
  const [topics, ministries] = await Promise.all([getAllTopics(), getAllMinistries()]);

  return (
    <>
      <IntroAnimation />
      <FeedExplorer topics={topics} ministries={ministries} />
    </>
  );
}
