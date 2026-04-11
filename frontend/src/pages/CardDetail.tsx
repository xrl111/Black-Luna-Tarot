import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { ArrowLeft, Star, Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { axiosClient, apiUrl } from "@/lib/api";

interface TarotCard {
  id: string;
  name: string;
  name_vi: string;
  suit: string;
  arcana: string;
  number: string;
  image_url: string;
  keywords: string[];
  meanings_light: string[];
  meanings_shadow: string[];
  fortune_telling: string[];
  questions_to_ask: string[];
  affirmation: string;
  archetype: string;
  numerology: string;
  elemental: string;
  mythical_spiritual: string;
  astrology: string;
}

const CardDetail = () => {
  const { id } = useParams<{ id: string }>();

  const {
    data: card,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["tarot-card", id],
    queryFn: async () => {
      const response = await axiosClient.get(
        apiUrl(`/api/v1/tarot-cards/${id}`)
      );
      return response.data as TarotCard;
    },
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Đang tải thông tin lá bài...</p>
        </div>
      </div>
    );
  }

  if (error || !card) {
    return (
      <div className="text-center space-y-4">
        <p className="text-destructive">Không tìm thấy lá bài</p>
        <Button asChild>
          <Link to="/cards">Quay lại danh sách</Link>
        </Button>
      </div>
    );
  }

  // Construct image URL
  const imageUrl = card.image_url
    ? apiUrl(`/api/v1/tarot-cards/image/${card.id}`)
    : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button asChild variant="outline" size="icon">
          <Link to="/cards">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div>
          <h1 className="text-3xl font-cinzel font-bold text-gradient">
            {card.name_vi}
          </h1>
          <p className="text-muted-foreground">{card.name}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Card Image */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-center">Hình ảnh lá bài</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="aspect-[2/3] bg-gradient-to-br from-mystic-100 to-gold-100 rounded-lg overflow-hidden">
                {imageUrl ? (
                  <img
                    src={imageUrl}
                    alt={card.name_vi}
                    className="h-full w-auto mx-auto object-contain"
                    onError={(e) => {
                      // Fallback to placeholder if image fails to load
                      const target = e.target as HTMLImageElement;
                      target.style.display = "none";
                      target.nextElementSibling?.classList.remove("hidden");
                    }}
                  />
                ) : null}
                <div
                  className={`w-full h-full flex items-center justify-center ${
                    imageUrl ? "hidden" : ""
                  }`}
                >
                  <span className="text-6xl"></span>
                </div>
              </div>
              <div className="mt-4 space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Bộ:</span>
                  <Badge variant="secondary">{card.suit}</Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Arcana:</span>
                  <Badge variant="outline">{card.arcana}</Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Số:</span>
                  <span className="font-semibold">{card.number}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Card Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Keywords */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="h-5 w-5" />
                Từ khóa
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {card.keywords.map((keyword: string, index: number) => (
                  <Badge key={index} variant="secondary">
                    {keyword}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Meanings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sun className="h-5 w-5 text-yellow-500" />Ý nghĩa thuận
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {card.meanings_light.map((meaning: string, index: number) => (
                    <li key={index} className="text-sm text-muted-foreground">
                      • {meaning}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Moon className="h-5 w-5 text-blue-500" />Ý nghĩa nghịch
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {card.meanings_shadow.map(
                    (meaning: string, index: number) => (
                      <li key={index} className="text-sm text-muted-foreground">
                        • {meaning}
                      </li>
                    )
                  )}
                </ul>
              </CardContent>
            </Card>
          </div>

          {/* Fortune Telling */}
          {card.fortune_telling && card.fortune_telling.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Bói toán</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {card.fortune_telling.map(
                    (fortune: string, index: number) => (
                      <li key={index} className="text-sm text-muted-foreground">
                        • {fortune}
                      </li>
                    )
                  )}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* Questions to Ask */}
          {card.questions_to_ask && card.questions_to_ask.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Câu hỏi để tự vấn</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {card.questions_to_ask.map(
                    (question: string, index: number) => (
                      <li key={index} className="text-sm text-muted-foreground">
                        • {question}
                      </li>
                    )
                  )}
                </ul>
              </CardContent>
            </Card>
          )}

          {/* Affirmation */}
          {card.affirmation && (
            <Card>
              <CardHeader>
                <CardTitle>Khẳng định</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-lg font-medium italic text-center text-primary">
                  "{card.affirmation}"
                </p>
              </CardContent>
            </Card>
          )}

          {/* Additional Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {card.archetype && (
              <Card>
                <CardHeader>
                  <CardTitle>Nguyên mẫu</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    {card.archetype}
                  </p>
                </CardContent>
              </Card>
            )}

            {card.numerology && (
              <Card>
                <CardHeader>
                  <CardTitle>Thần số học</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    {card.numerology}
                  </p>
                </CardContent>
              </Card>
            )}

            {card.elemental && (
              <Card>
                <CardHeader>
                  <CardTitle>Nguyên tố</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    {card.elemental}
                  </p>
                </CardContent>
              </Card>
            )}

            {card.astrology && (
              <Card>
                <CardHeader>
                  <CardTitle>Chiêm tinh</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    {card.astrology}
                  </p>
                </CardContent>
              </Card>
            )}
          </div>

          {card.mythical_spiritual && (
            <Card>
              <CardHeader>
                <CardTitle>Huyền thoại & Tâm linh</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {card.mythical_spiritual}
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center gap-4 pt-6">
        <Button asChild>
          <Link to="/reading">Bắt đầu xem bói</Link>
        </Button>
        <Button asChild variant="outline">
          <Link to="/cards">Xem tất cả lá bài</Link>
        </Button>
      </div>
    </motion.div>
  );
};

export default CardDetail;
