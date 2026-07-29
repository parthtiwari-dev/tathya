"use client";

import { useLanguage } from "@/lib/i18n";

const heading = { en: "Mission & Ethics", hi: "मिशन और नैतिकता" };

const paragraphs = [
  {
    en: "Tathya is an autonomous civic record of India's Union Government. It watches a fixed list of public sources, stores immutable snapshots of what those sources published, and later groups related material into sourced case files. It does not decide which political stories matter by hand, and it does not publish verdicts on whether a claim is true or false.",
    hi: "तथ्य भारत की केंद्र सरकार का एक स्वायत्त नागरिक अभिलेख है। यह सार्वजनिक स्रोतों की एक निश्चित सूची पर नज़र रखता है, उन स्रोतों द्वारा प्रकाशित सामग्री के अपरिवर्तनीय स्नैपशॉट संग्रहीत करता है, और बाद में संबंधित सामग्री को स्रोत-आधारित केस फ़ाइलों में समूहित करता है। यह हाथ से यह तय नहीं करता कि कौन-सी राजनीतिक कहानियाँ महत्वपूर्ण हैं, और न ही यह इस बारे में फ़ैसला सुनाता है कि कोई दावा सही है या ग़लत।",
  },
  {
    en: "A cluster of signals becomes a public case file only when it crosses a fixed significance threshold — independent source count, speed of new coverage, and confirmation from more than one type of source. No person decides this on a per-story basis.",
    hi: "संकेतों का कोई समूह तभी एक सार्वजनिक केस फ़ाइल बनता है जब वह एक निश्चित महत्व सीमा को पार करता है — स्वतंत्र स्रोतों की संख्या, नई कवरेज की गति, और एक से अधिक प्रकार के स्रोतों से पुष्टि। यह निर्णय हर कहानी के लिए अलग से कोई व्यक्ति नहीं लेता।",
  },
  {
    en: "The central promise is narrow and strict: record what was said, who said it, when it was said, and what primary documents can verify. A government claim, an opposition claim, an independent media report, and a citizen statement may sit side by side, but the system must never disguise interpretation as fact. The Verifiable Facts panel is reserved for primary records such as PIB releases, Parliament answers, gazette material, datasets, and similar documents.",
    hi: "केंद्रीय प्रतिबद्धता सीमित और सख़्त है: यह दर्ज करना कि क्या कहा गया, किसने कहा, कब कहा गया, और कौन-से प्राथमिक दस्तावेज़ इसकी पुष्टि कर सकते हैं। सरकार का दावा, विपक्ष का दावा, स्वतंत्र मीडिया की रिपोर्ट, और किसी नागरिक का बयान एक साथ रखे जा सकते हैं, लेकिन यह प्रणाली व्याख्या को कभी तथ्य के रूप में प्रस्तुत नहीं करेगी। सत्यापन योग्य तथ्य पैनल केवल PIB विज्ञप्तियों, संसद के उत्तरों, राजपत्र सामग्री, डेटासेट और इसी तरह के प्राथमिक अभिलेखों के लिए आरक्षित है।",
  },
  {
    en: "Every public claim, event, fact, summary line, and correction must point back to stored source material. If the original page is edited, deleted, or disappears, the ingestion-time snapshot remains the audit trail. Snapshots are for accountability and reproducibility; they are not a license to republish entire copyrighted articles publicly without review.",
    hi: "हर सार्वजनिक दावा, घटना, तथ्य, सारांश पंक्ति, और सुधार संग्रहीत स्रोत सामग्री की ओर वापस इंगित करना चाहिए। यदि मूल पृष्ठ संपादित किया जाता है, हटा दिया जाता है, या ग़ायब हो जाता है, तो संग्रहण-समय का स्नैपशॉट ही ऑडिट ट्रेल बना रहता है। स्नैपशॉट जवाबदेही और पुनरुत्पादन-योग्यता के लिए हैं; वे बिना समीक्षा के संपूर्ण कॉपीराइट लेखों को सार्वजनिक रूप से फिर से प्रकाशित करने का लाइसेंस नहीं हैं।",
  },
  {
    en: "Tathya protects ordinary private citizens from unnecessary exposure. Public officials, elected representatives, parties, ministries, public spokespeople, and self-identified public actors can be resolved as entities. Private bystanders, incidental names, and people only visible because they were captured in footage should not be expanded into profiles or cross-referenced beyond the public source itself.",
    hi: "तथ्य सामान्य निजी नागरिकों को अनावश्यक रूप से उजागर होने से बचाता है। सार्वजनिक अधिकारी, निर्वाचित प्रतिनिधि, राजनीतिक दल, मंत्रालय, सार्वजनिक प्रवक्ता, और स्वयं-घोषित सार्वजनिक व्यक्ति संस्थाओं (entities) के रूप में पहचाने जा सकते हैं। निजी दर्शक, आकस्मिक रूप से आए नाम, और केवल फ़ुटेज में दिख जाने के कारण दिखने वाले लोगों को प्रोफ़ाइल में विस्तारित नहीं किया जाना चाहिए या मूल सार्वजनिक स्रोत से आगे क्रॉस-रेफ़रेंस नहीं किया जाना चाहिए।",
  },
  {
    en: "Corrections are for Tathya's own mechanical mistakes: a wrong date, merged entity, incorrect attribution, broken source link, or extraction error. Corrections are not a route for political disputes about whether a source's statement is correct. A correction history should be visible and append-only.",
    hi: "सुधार केवल तथ्य की अपनी यांत्रिक ग़लतियों के लिए हैं: ग़लत तारीख़, आपस में मिली हुई संस्थाएँ, ग़लत आरोपण, टूटा हुआ स्रोत लिंक, या निष्कर्षण में त्रुटि। सुधार इस बारे में राजनीतिक विवादों का रास्ता नहीं हैं कि किसी स्रोत का बयान सही है या नहीं। सुधार का इतिहास दृश्यमान और केवल-जोड़े-जाने-योग्य होना चाहिए।",
  },
  {
    en: "The project stays open source under AGPL-3.0 so the scoring, clustering, and generation logic can be inspected by people who disagree with one another. Hosting and data storage should not depend on any single point of failure; the record is built to survive pressure to take it down, not just to survive the founder losing interest. The system earns trust through boring discipline: fixed source rules, append-only evidence, symmetric treatment of political actors, and no private editorial shortcuts.",
    hi: "यह परियोजना AGPL-3.0 के तहत ओपन सोर्स बनी रहती है ताकि स्कोरिंग, क्लस्टरिंग और जनरेशन का तर्क उन लोगों द्वारा भी जाँचा जा सके जो आपस में असहमत हैं। होस्टिंग और डेटा भंडारण किसी एक इकलौते विफलता बिंदु पर निर्भर नहीं होने चाहिए; यह अभिलेख इसे हटाने के दबाव को झेलने के लिए बनाया गया है, न कि केवल संस्थापक की रुचि ख़त्म होने तक टिकने के लिए। यह प्रणाली भरोसा उबाऊ अनुशासन से अर्जित करती है: तय स्रोत नियम, केवल-जोड़े-जाने-योग्य साक्ष्य, राजनीतिक पक्षों के प्रति सममित व्यवहार, और कोई निजी संपादकीय छूट नहीं।",
  },
];

export default function AboutPage() {
  const { lang } = useLanguage();

  return (
    <article className="max-w-2xl py-10 sm:py-12">
      <h1 className="font-serif text-2xl font-medium text-ink sm:text-3xl">{heading[lang]}</h1>

      <div className="mt-6 space-y-5">
        {paragraphs.map((paragraph, i) => (
          <p key={i} className="text-[15px] leading-relaxed text-ink-secondary">
            {paragraph[lang]}
          </p>
        ))}
      </div>
    </article>
  );
}
