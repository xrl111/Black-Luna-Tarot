import { useState } from "react";
import SEO from "@/components/SEO";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Search, Filter, Grid, List, Flame, Droplets, Wind, Mountain, ImageIcon } from "lucide-react";
import { ToggleGroup } from "@/components/ui/toggle-button";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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
}

interface PaginatedResponse {
  items: TarotCard[];
  total: number;
  page: number;
  limit: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

const TarotCards = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedSuit, setSelectedSuit] = useState("all");
  const [selectedCardType, setSelectedCardType] = useState("all");
  const [selectedElement, setSelectedElement] = useState("all");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(12);

  // Build query parameters based on filters
  const buildQueryParams = () => {
    const params = new URLSearchParams();
    params.append("page", currentPage.toString());
    params.append("limit", pageSize.toString());

    if (searchTerm) params.append("search", searchTerm);
    if (selectedSuit !== "all") params.append("suit", selectedSuit);
    if (selectedCardType !== "all")
      params.append("card_type", selectedCardType);
    if (selectedElement !== "all") params.append("element", selectedElement);

    return params.toString();
  };

  const {
    data: cardsData,
    isLoading,
    error,
  } = useQuery({
    queryKey: [
      "tarot-cards",
      searchTerm,
      selectedSuit,
      selectedCardType,
      selectedElement,
      currentPage,
    ],
    queryFn: async () => {
      const queryParams = buildQueryParams();
      const response = await axiosClient.get(
        apiUrl(`/api/v1/tarot-cards/?${queryParams}`)
      );
      return response.data as PaginatedResponse;
    },
  });

  const cards = cardsData?.items || [];
  const totalPages = cardsData?.pages || 1;

  const suits = [
    { value: "all", label: "Tất cả bộ" },
    { value: "wands", label: "Gậy (Wands)" },
    { value: "cups", label: "Cốc (Cups)" },
    { value: "swords", label: "Kiếm (Swords)" },
    { value: "pentacles", label: "Đồng tiền (Pentacles)" },
    { value: "major", label: "Major Arcana" },
  ];

  const cardTypes = [
    { value: "all", label: "Tất cả loại" },
    { value: "major", label: "Major Arcana" },
    { value: "minor", label: "Minor Arcana" },
  ];

  const elements = [
    { value: "all", label: "Tất cả nguyên tố", icon: null },
    { value: "fire", label: "Lửa (Fire)", icon: Flame },
    { value: "water", label: "Nước (Water)", icon: Droplets },
    { value: "air", label: "Khí (Air)", icon: Wind },
    { value: "earth", label: "Đất (Earth)", icon: Mountain },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Đang tải bộ bài...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center space-y-4">
        <p className="text-destructive">Có lỗi xảy ra khi tải dữ liệu</p>
        <Button onClick={() => window.location.reload()}>Thử lại</Button>
      </div>
    );
  }

  return (
    <>
      <SEO
        title="Bộ bài Tarot - Black Luna Tarot"
        description="Duyệt 78 lá bài Tarot, xem ý nghĩa chi tiết, lọc theo bộ, loại và nguyên tố."
        keywords={["tarot", "bộ bài", "78 lá", "Black Luna Tarot"]}
        url="https://example.com/cards"
      />
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="space-y-6"
      >
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-cinzel font-bold text-gradient">
            Bộ bài Tarot
          </h1>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Khám phá 78 lá bài Tarot với ý nghĩa chi tiết. Sử dụng các bộ lọc để
            tìm lá bài phù hợp.
          </p>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Filter className="h-5 w-5" />
              Bộ lọc & Tìm kiếm
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 items-end">
              <div className="relative lg:col-span-2">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Tìm kiếm lá bài..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 h-10"
                />
              </div>

              <Select value={selectedSuit} onValueChange={setSelectedSuit}>
                <SelectTrigger className="tarot-select-trigger">
                  <SelectValue placeholder="Chọn bộ" />
                </SelectTrigger>
                <SelectContent className="tarot-select-content">
                  {suits.map((suit) => (
                    <SelectItem
                      key={suit.value}
                      value={suit.value}
                      className="tarot-select-item"
                    >
                      {suit.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select
                value={selectedCardType}
                onValueChange={setSelectedCardType}
              >
                <SelectTrigger className="tarot-select-trigger">
                  <SelectValue placeholder="Chọn loại" />
                </SelectTrigger>
                <SelectContent className="tarot-select-content">
                  {cardTypes.map((type) => (
                    <SelectItem
                      key={type.value}
                      value={type.value}
                      className="tarot-select-item"
                    >
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select
                value={selectedElement}
                onValueChange={setSelectedElement}
              >
                <SelectTrigger className="tarot-select-trigger">
                  <SelectValue placeholder="Chọn nguyên tố" />
                </SelectTrigger>
                <SelectContent className="tarot-select-content">
                  {elements.map((element) => {
                    const Icon = element.icon;
                    return (
                      <SelectItem
                        key={element.value}
                        value={element.value}
                        className="tarot-select-item"
                      >
                        <div className="flex items-center gap-2">
                          {Icon && <Icon className="w-4 h-4 text-muted-foreground" />}
                          {element.label}
                        </div>
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>

              <ToggleGroup
                value={viewMode}
                onValueChange={(value) => setViewMode(value as "grid" | "list")}
                options={[
                  { value: "grid", icon: <Grid className="h-4 w-4" /> },
                  { value: "list", icon: <List className="h-4 w-4" /> },
                ]}
                variant="default"
                size="icon"
              />
            </div>
          </CardContent>
        </Card>

        {/* Results */}
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <p className="text-muted-foreground">
              Tìm thấy {cardsData?.total || 0} lá bài
            </p>
            <p className="text-muted-foreground">
              Trang {currentPage} / {totalPages}
            </p>
          </div>

          {viewMode === "grid" ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {cards.map((card: TarotCard, index: number) => {
                const imageUrl = card.image_url
                  ? apiUrl(`/api/v1/tarot-cards/image/${card.id}`)
                  : null;

                return (
                  <motion.div
                    key={card.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05, duration: 0.3 }}
                  >
                    <Card className="h-full hover:shadow-lg transition-shadow duration-300">
                      <CardHeader className="text-center pb-2">
                        <div className="w-full h-48 bg-gradient-to-br from-mystic-100 to-gold-100 rounded-lg mb-3 overflow-hidden">
                          {imageUrl ? (
                            <img
                              src={imageUrl}
                              alt={card.name_vi}
                              className="h-full w-auto mx-auto object-contain"
                              onError={(e) => {
                                // Fallback to placeholder if image fails to load
                                const target = e.target as HTMLImageElement;
                                target.style.display = "none";
                                target.nextElementSibling?.classList.remove(
                                  "hidden"
                                );
                              }}
                            />
                          ) : null}
                          <div
                            className={`w-full h-full flex items-center justify-center ${
                              imageUrl ? "hidden" : ""
                            }`}
                          >
                            <ImageIcon className="w-12 h-12 text-muted-foreground/30" />
                          </div>
                        </div>
                        <CardTitle className="font-cinzel text-lg">
                          {card.name_vi}
                        </CardTitle>
                        <CardDescription>{card.name}</CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="flex flex-wrap gap-2">
                          <Badge variant="secondary">{card.suit}</Badge>
                          <Badge variant="outline">{card.arcana}</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground line-clamp-3">
                          {card.keywords.slice(0, 3).join(", ")}
                        </p>
                        <Button asChild className="w-full">
                          <Link to={`/cards/${card.id}`}>Xem chi tiết</Link>
                        </Button>
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
            </div>
          ) : (
            <div className="space-y-4">
              {cards.map((card: TarotCard, index: number) => {
                const imageUrl = card.image_url
                  ? apiUrl(`/api/v1/tarot-cards/image/${card.id}`)
                  : null;

                return (
                  <motion.div
                    key={card.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05, duration: 0.3 }}
                  >
                    <Card>
                      <CardContent className="p-6">
                        <div className="flex items-center gap-4">
                          <div className="w-16 h-24 bg-gradient-to-br from-mystic-100 to-gold-100 rounded-lg overflow-hidden flex-shrink-0">
                            {imageUrl ? (
                              <img
                                src={imageUrl}
                                alt={card.name_vi}
                                className="h-full w-auto mx-auto object-contain"
                                onError={(e) => {
                                  // Fallback to placeholder if image fails to load
                                  const target = e.target as HTMLImageElement;
                                  target.style.display = "none";
                                  target.nextElementSibling?.classList.remove(
                                    "hidden"
                                  );
                                }}
                              />
                            ) : null}
                            <div
                              className={`w-full h-full flex items-center justify-center ${
                                imageUrl ? "hidden" : ""
                              }`}
                            >
                              <ImageIcon className="w-8 h-8 text-muted-foreground/30" />
                            </div>
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h3 className="font-cinzel text-lg font-semibold">
                                {card.name_vi}
                              </h3>
                              <Badge variant="secondary">{card.suit}</Badge>
                              <Badge variant="outline">{card.arcana}</Badge>
                            </div>
                            <p className="text-muted-foreground mb-2">
                              {card.name}
                            </p>
                            <p className="text-sm text-muted-foreground">
                              {card.keywords.slice(0, 5).join(", ")}
                            </p>
                          </div>
                          <Button asChild>
                            <Link to={`/cards/${card.id}`}>Xem chi tiết</Link>
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center gap-2 mt-8">
              <Button
                variant="outline"
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
              >
                Trước
              </Button>
              <span className="flex items-center px-4 text-muted-foreground">
                {currentPage} / {totalPages}
              </span>
              <Button
                variant="outline"
                onClick={() =>
                  setCurrentPage(Math.min(totalPages, currentPage + 1))
                }
                disabled={currentPage === totalPages}
              >
                Sau
              </Button>
            </div>
          )}
        </div>
      </motion.div>
    </>
  );
};

export default TarotCards;
