import type { Claim, Topic, TopicSummary } from "./types";

// Mock fixtures shaped exactly like the intended API v1 response contract
// (see lib/types.ts). Once /api/topics and /api/topics/[slug] exist for real,
// these functions are replaced by fetch() calls with no change to any component.

const topics: Topic[] = [
  {
    id: "t1",
    slug: "cjp-sansad-chalo-parliament-march",
    title: "CJP's 'Sansad Chalo': protest march reaches Parliament",
    summary:
      "A citizens' collective under the banner 'Sansad Chalo' organized a march toward Parliament, coinciding with an ongoing hunger strike by an activist. Delhi Police denied permission for the march citing law-and-order concerns, while organizers said the protest would proceed regardless.",
    status: "live",
    ministry: "Home Affairs",
    ministrySlug: "home-affairs",
    entityTags: ["Parliament", "Delhi Police", "Sonam Wangchuk"],
    firstSeen: "2026-07-17T09:10:00+05:30",
    lastSignalAt: "2026-07-19T21:37:00+05:30",
    sourceCount: { official: 1, media: 4, citizen: 2 },
    claims: [
      {
        id: "c1",
        claimText:
          "Delhi Police said no permission had been granted for the march and that appropriate legal action would follow any attempt to proceed.",
        sourceType: "government",
        quotedSpan: "no permission has been granted for the proposed march",
        sourceName: "Hindustan Times",
        sourceUrl:
          "https://www.hindustantimes.com/india-news/cjps-sansad-chalo-what-to-expect-on-monday-as-protesters-set-for-parliament-march-police-say-no-permission-101784475581879.html",
        sourceKey: "hindustan-times-india",
        publishedAt: "2026-07-19T16:07:56+00:00",
      },
      {
        id: "c2",
        claimText:
          "The activist's wife said he was prepared to end his hunger strike only if a specific condition set by the family was met.",
        sourceType: "citizen",
        quotedSpan: "ready to end his hunger strike, says wife, sets condition",
        sourceName: "Hindustan Times",
        sourceUrl:
          "https://www.hindustantimes.com/india-news/wangchuk-is-ready-to-end-his-hunger-strike-says-wife-sets-condition-ahead-of-cockroach-janta-party-march-to-parliament-101784474448090.html",
        sourceKey: "hindustan-times-india",
        publishedAt: "2026-07-19T15:26:21+00:00",
      },
      {
        id: "c3",
        claimText:
          "Organizers said the march would go ahead as planned regardless of the denial of permission.",
        sourceType: "citizen",
        quotedSpan: "the march to Parliament will proceed as scheduled",
        sourceName: "Indian Express",
        sourceUrl: "https://indianexpress.com/section/india/",
        sourceKey: "indian-express-india",
        publishedAt: "2026-07-19T18:40:00+00:00",
      },
    ],
    events: [
      { id: "e1", eventDate: "2026-07-17", description: "Hunger strike by activist Sonam Wangchuk continues; supporters begin gathering ahead of the planned march.", sourceSignalIds: ["s101"] },
      { id: "e2", eventDate: "2026-07-19", description: "Delhi Police publicly state that permission for the Parliament march has not been granted.", sourceSignalIds: ["s108"] },
      { id: "e3", eventDate: "2026-07-19", description: "A Delhi hospital's request to shift the activist to another facility is denied by the High Court.", sourceSignalIds: ["s110"] },
    ],
    facts: [],
    relations: [
      { id: "r1", relatedTopicSlug: "neet-leak-education-minister-meeting", relatedTopicTitle: "NEET leak fallout: education minister meets topper amid resignation demands", relationType: "same_policy_area" },
    ],
    history: [
      { id: "h1", type: "status_changed", description: "Topic promoted from raw_cluster to live (5 independent sources, official + citizen presence confirmed).", timestamp: "2026-07-17T10:00:00+05:30" },
      { id: "h2", type: "event_added", description: "Event added: hunger strike continues, supporters gather.", timestamp: "2026-07-17T10:05:00+05:30" },
      { id: "h3", type: "claim_added", description: "Claim added from Delhi Police statement (government).", timestamp: "2026-07-19T16:10:00+05:30" },
      { id: "h4", type: "claim_added", description: "Claim added from activist's family (citizen).", timestamp: "2026-07-19T15:30:00+05:30" },
    ],
    openQuestions: [
      { id: "oq1", question: "The march's legal permission status is disputed between organizers and police — no court order confirming either account has entered Verifiable Facts yet.", relatedClaimId: "c1" },
    ],
    contradictions: [],
  },
  {
    id: "t2",
    slug: "vikram-1-hydrogen-train-twin-milestones",
    title: "India marks twin milestones: Vikram-1 launch and first hydrogen train",
    summary:
      "Within a 48-hour window, India recorded two infrastructure milestones: the Vikram-1 rocket launch and the flagging-off of the country's first hydrogen-powered train between Jind and Sonipat, both presented by the government as markers of technological progress.",
    status: "live",
    ministry: "Railways",
    ministrySlug: "railways",
    entityTags: ["PMO", "Ministry of Railways", "ISRO"],
    firstSeen: "2026-07-17T07:00:00+05:30",
    lastSignalAt: "2026-07-19T19:12:00+05:30",
    sourceCount: { official: 2, media: 3, citizen: 0 },
    claims: [
      {
        id: "c4",
        claimText: "The Prime Minister's Office described the hydrogen train as a milestone for clean-energy transport in India.",
        sourceType: "government",
        quotedSpan: "Historic! PM Modi Flags Off India's First Hydrogen-Powered Train",
        sourceName: "PMO (YouTube)",
        sourceUrl: "https://www.youtube.com/watch?v=XDskGdA9opo",
        sourceKey: "pmo-youtube",
        publishedAt: "2026-07-17T07:30:39+00:00",
      },
      {
        id: "c5",
        claimText: "Independent coverage noted the train runs the Jind–Sonipat route and framed it alongside the Vikram-1 launch as a 48-hour double milestone.",
        sourceType: "media",
        quotedSpan: "twin milestones under 48 hours",
        sourceName: "Hindustan Times",
        sourceUrl: "https://www.hindustantimes.com/india-news/in-space-and-on-track-india-marks-twin-milestones-under-48-hours-with-vikram-1-launch-first-hydrogen-train-101784465851436.html",
        sourceKey: "hindustan-times-india",
        publishedAt: "2026-07-19T13:42:09+00:00",
      },
    ],
    events: [
      { id: "e4", eventDate: "2026-07-17", description: "Hydrogen-powered train flagged off between Jind and Sonipat.", sourceSignalIds: ["s201"] },
      { id: "e5", eventDate: "2026-07-18", description: "Vikram-1 rocket launch reported alongside continued coverage of the train rollout.", sourceSignalIds: ["s205"] },
    ],
    facts: [
      { id: "f1", factText: "The hydrogen train's first operational route runs between Jind and Sonipat railway stations.", primaryDocUrl: "https://pib.gov.in/", docType: "pib", quotedSpan: "Jind and Sonipat at Jind railway station" },
    ],
    relations: [],
    history: [
      { id: "h5", type: "status_changed", description: "Topic promoted from raw_cluster to live.", timestamp: "2026-07-17T08:00:00+05:30" },
      { id: "h6", type: "fact_added", description: "Verifiable fact added from official release confirming the route.", timestamp: "2026-07-17T09:00:00+05:30" },
    ],
    openQuestions: [],
    contradictions: [],
  },
  {
    id: "t3",
    slug: "neet-leak-education-minister-meeting",
    title: "NEET leak fallout: education minister meets topper amid resignation demands",
    summary:
      "Following allegations of a paper leak in the NEET medical entrance exam, opposition figures have called for the education minister's resignation. The minister met with the exam's topper amid the controversy; the exact content of that meeting is disputed between government and opposition accounts.",
    status: "live",
    ministry: "Education",
    ministrySlug: "education",
    entityTags: ["Ministry of Education", "NEET", "Dharmendra Pradhan"],
    firstSeen: "2026-07-18T11:00:00+05:30",
    lastSignalAt: "2026-07-19T15:05:59+00:00",
    sourceCount: { official: 0, media: 2, citizen: 0 },
    claims: [
      {
        id: "c6",
        claimText: "Opposition leader Derek O'Brien wrote to the Prime Minister asking for an all-party meeting on the matter, alongside delimitation and FCRA bills.",
        sourceType: "opposition",
        quotedSpan: "Convene all-party meet on delimitation, FCRA bills",
        sourceName: "Hindustan Times",
        sourceUrl: "https://www.hindustantimes.com/india-news/convene-all-party-meet-on-delimitation-fcra-bills-derek-obrien-to-pm-modi-101784459445155.html",
        sourceKey: "hindustan-times-india",
        publishedAt: "2026-07-19T12:49:22+00:00",
      },
      {
        id: "c7",
        claimText: "Coverage reported the education minister met with the exam topper amid ongoing calls for his resignation over the leak allegations.",
        sourceType: "media",
        quotedSpan: "education minister Pradhan's meeting with topper",
        sourceName: "Hindustan Times",
        sourceUrl: "https://www.hindustantimes.com/india-news/amid-fiery-demands-for-his-resignation-over-neet-leak-education-minister-pradhans-meeting-with-topper-101784472721199.html",
        sourceKey: "hindustan-times-india",
        publishedAt: "2026-07-19T15:05:59+00:00",
      },
    ],
    events: [
      { id: "e6", eventDate: "2026-07-18", description: "Opposition figures publicly demand the education minister's resignation over leak allegations.", sourceSignalIds: ["s301"] },
      { id: "e7", eventDate: "2026-07-19", description: "Education minister meets with the exam topper; meeting details reported without official government readout.", sourceSignalIds: ["s305"] },
    ],
    facts: [],
    relations: [
      { id: "r2", relatedTopicSlug: "cjp-sansad-chalo-parliament-march", relatedTopicTitle: "CJP's 'Sansad Chalo': protest march reaches Parliament", relationType: "same_policy_area" },
    ],
    history: [
      { id: "h7", type: "status_changed", description: "Topic promoted from raw_cluster to live.", timestamp: "2026-07-18T12:00:00+05:30" },
      { id: "h8", type: "claim_added", description: "Claim added from opposition statement.", timestamp: "2026-07-19T13:00:00+05:30" },
      { id: "h9", type: "claim_added", description: "Claim added from media coverage of minister-topper meeting.", timestamp: "2026-07-19T15:10:00+05:30" },
    ],
    openQuestions: [
      { id: "oq2", question: "No official government statement confirming or denying a leak has entered Verifiable Facts — only opposition claims and media reporting exist so far.", relatedClaimId: "c6" },
    ],
    contradictions: [
      {
        id: "cx1",
        entity: "Ministry of Education (spokesperson)",
        statementA: { text: "Initial ministry statement said no evidence of a paper leak had been found.", date: "2026-07-15", sourceName: "Hindustan Times", sourceUrl: "https://www.hindustantimes.com/india-news/" },
        statementB: { text: "A later ministry statement described an 'isolated incident' now under investigation.", date: "2026-07-18", sourceName: "Indian Express", sourceUrl: "https://indianexpress.com/section/india/" },
      },
    ],
  },
  {
    id: "t4",
    slug: "rbi-monetary-penalty-payment-banks-kyc",
    title: "RBI imposes monetary penalty on payment banks over KYC lapses",
    summary:
      "The Reserve Bank of India imposed monetary penalties on a group of payment banks for deficiencies in customer due-diligence and KYC norms, based on the regulator's own compliance review.",
    status: "live",
    ministry: "Finance",
    ministrySlug: "finance",
    entityTags: ["RBI", "Payment Banks", "KYC"],
    firstSeen: "2026-07-14T10:00:00+05:30",
    lastSignalAt: "2026-07-18T12:30:00+05:30",
    sourceCount: { official: 1, media: 2, citizen: 0 },
    claims: [
      {
        id: "c8",
        claimText: "RBI said the penalties were based on deficiencies found in regulatory compliance, not on customer transactions.",
        sourceType: "government",
        quotedSpan: "penalty is based on deficiencies in regulatory compliance",
        sourceName: "RBI Press Releases",
        sourceUrl: "https://www.rbi.org.in/",
        sourceKey: "rbi-press-releases",
        publishedAt: "2026-07-14T10:15:00+00:00",
      },
      {
        id: "c9",
        claimText: "Financial press reported the penalty amount and named the affected payment banks.",
        sourceType: "media",
        quotedSpan: "RBI imposes monetary penalty on payment banks",
        sourceName: "Indian Express",
        sourceUrl: "https://indianexpress.com/section/business/",
        sourceKey: "indian-express-india",
        publishedAt: "2026-07-14T14:00:00+00:00",
      },
    ],
    events: [
      { id: "e8", eventDate: "2026-07-14", description: "RBI publishes the penalty order against the named payment banks.", sourceSignalIds: ["s401"] },
    ],
    facts: [
      { id: "f2", factText: "RBI's order cites specific KYC and customer due-diligence provisions as the basis for the penalty.", primaryDocUrl: "https://www.rbi.org.in/", docType: "dataset", quotedSpan: "deficiencies in regulatory compliance" },
    ],
    relations: [],
    history: [
      { id: "h10", type: "status_changed", description: "Topic promoted from raw_cluster to live.", timestamp: "2026-07-14T11:00:00+05:30" },
      { id: "h11", type: "fact_added", description: "Verifiable fact added directly from RBI's order.", timestamp: "2026-07-14T11:30:00+05:30" },
    ],
    openQuestions: [],
    contradictions: [],
  },
  {
    id: "t5",
    slug: "pm-kisan-installment-release-delay",
    title: "PM-KISAN installment release faces regional delays",
    summary:
      "The release of a scheduled PM-KISAN installment saw regional delays reported across several states earlier this year. No new signals have linked to this topic in over 60 days.",
    status: "archived",
    ministry: "Agriculture",
    ministrySlug: "agriculture",
    entityTags: ["PM-KISAN", "Ministry of Agriculture"],
    firstSeen: "2026-04-02T09:00:00+05:30",
    lastSignalAt: "2026-05-10T09:00:00+05:30",
    sourceCount: { official: 1, media: 3, citizen: 1 },
    claims: [
      {
        id: "c10",
        claimText: "The ministry attributed the delay to a routine beneficiary-list verification cycle.",
        sourceType: "government",
        quotedSpan: "routine verification of the beneficiary list",
        sourceName: "Indian Express",
        sourceUrl: "https://indianexpress.com/section/india/",
        sourceKey: "indian-express-india",
        publishedAt: "2026-04-05T09:00:00+00:00",
      },
    ],
    events: [
      { id: "e9", eventDate: "2026-04-02", description: "Reports of delayed installment release begin surfacing from multiple states.", sourceSignalIds: ["s501"] },
      { id: "e10", eventDate: "2026-05-10", description: "Ministry statement attributes the delay to beneficiary-list verification; coverage tapers off after this point.", sourceSignalIds: ["s520"] },
    ],
    facts: [],
    relations: [],
    history: [
      { id: "h12", type: "status_changed", description: "Topic promoted from raw_cluster to live.", timestamp: "2026-04-02T10:00:00+05:30" },
      { id: "h13", type: "status_changed", description: "Archived after 60 days with no new linked signal.", timestamp: "2026-07-09T00:00:00+05:30" },
    ],
    openQuestions: [],
    contradictions: [],
  },
];

export function getAllTopics(): TopicSummary[] {
  return topics
    .slice()
    .sort((a, b) => (a.lastSignalAt < b.lastSignalAt ? 1 : -1))
    .map(({ id, slug, title, summary, status, ministry, ministrySlug, entityTags, lastSignalAt, sourceCount }) => ({
      id,
      slug,
      title,
      summary,
      status,
      ministry,
      ministrySlug,
      entityTags,
      lastSignalAt,
      sourceCount,
    }));
}

export function getTopicBySlug(slug: string): Topic | undefined {
  return topics.find((topic) => topic.slug === slug);
}

export function getTopicsByMinistry(ministrySlug: string): TopicSummary[] {
  return getAllTopics().filter((topic) => topic.ministrySlug === ministrySlug);
}

export function getAllMinistries(): { name: string; slug: string }[] {
  const seen = new Map<string, string>();
  for (const topic of topics) seen.set(topic.ministrySlug, topic.ministry);
  return Array.from(seen, ([slug, name]) => ({ slug, name }));
}

export function getClaimsBySourceKey(sourceKey: string): (Claim & { topicSlug: string; topicTitle: string })[] {
  const results: (Claim & { topicSlug: string; topicTitle: string })[] = [];
  for (const topic of topics) {
    for (const claim of topic.claims) {
      if (claim.sourceKey === sourceKey) {
        results.push({ ...claim, topicSlug: topic.slug, topicTitle: topic.title });
      }
    }
  }
  return results.sort((a, b) => (a.publishedAt < b.publishedAt ? 1 : -1));
}
