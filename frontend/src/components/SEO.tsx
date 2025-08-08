import React from "react";

type SEOProps = {
  title?: string;
  description?: string;
  keywords?: string[];
  url?: string;
  image?: string;
  locale?: string; // vi_VN
  type?: "website" | "article";
  noindex?: boolean;
};

export const SEO: React.FC<SEOProps> = ({
  title = "Black Luna Tarot - AI-Powered Tarot Reading",
  description = "Hệ thống Tarot dùng LLM, đưa ra giải thích sâu sắc và cá nhân hoá bằng tiếng Việt.",
  keywords = [
    "tarot",
    "AI tarot",
    "Black Luna Tarot",
    "LLM",
    "xem bói tarot",
    "tiếng Việt",
  ],
  url = "https://example.com",
  image = "/vite.svg",
  locale = "vi_VN",
  type = "website",
  noindex = false,
}) => {
  const safeTitle = title?.slice(0, 120);
  const safeDesc = description?.slice(0, 160);
  const content = keywords?.join(", ");
  return (
    <>
      <title>{safeTitle}</title>
      <meta name="description" content={safeDesc} />
      {content && <meta name="keywords" content={content} />}
      {noindex && <meta name="robots" content="noindex, nofollow" />}

      {/* Open Graph */}
      <meta property="og:title" content={safeTitle} />
      <meta property="og:description" content={safeDesc} />
      <meta property="og:type" content={type} />
      <meta property="og:url" content={url} />
      <meta property="og:image" content={image} />
      <meta property="og:locale" content={locale} />

      {/* Twitter Cards */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={safeTitle} />
      <meta name="twitter:description" content={safeDesc} />
      <meta name="twitter:image" content={image} />
    </>
  );
};

export default SEO;
