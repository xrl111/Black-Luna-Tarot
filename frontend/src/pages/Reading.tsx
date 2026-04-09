import { useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Sparkles, Shuffle, Save, Eye, Settings, Wand2, Image as ImageIcon } from "lucide-react";
import { LLMSettingsModal } from "@/components/LLMSettingsModal";
import SEO from "@/components/SEO";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import TarotMarkdownViewer from "@/components/TarotMarkdownViewer";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { axiosClient, apiUrl } from "@/lib/api";
import { ToggleGroup } from "@/components/ui/toggle-button";
import BackImage from "@/assets/Back.jpg";

interface TarotCard {
  id: string;
  name: string;
  name_vi: string;
  suit: string;
  arcana: string;
  number: string;
  image_url: string;
  keywords: string[];
  // Added for detailed reading
  is_reversed?: boolean;
  order_index?: number;
}

interface ReadingResult {
  question: string;
  cards: TarotCard[];
  ai_response: string;
  session_id: string;
}

const Reading = () => {
  const [question, setQuestion] = useState("");
  const [readingType, setReadingType] = useState("3");
  const [isGenerating, setIsGenerating] = useState(false);
  const [readingResult, setReadingResult] = useState<ReadingResult | null>(
    null
  );
  const { user } = useAuth();
  const [drawMode, setDrawMode] = useState<"auto" | "manual">("auto");
  const [selectedCards, setSelectedCards] = useState<TarotCard[]>([]);
  const [drawnCards, setDrawnCards] = useState<TarotCard[]>([]);
  const [selectionLocked, setSelectionLocked] = useState<boolean>(false);
  const [shuffledDeck, setShuffledDeck] = useState<TarotCard[]>([]);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [intakeResult, setIntakeResult] = useState<{name: string, reason: string} | null>(null);
  const [isIntaking, setIsIntaking] = useState(false);
  const resultRef = useRef<HTMLDivElement | null>(null);
  const readingRef = useRef<HTMLDivElement | null>(null);
  const [streamingText, setStreamingText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const targetCount = useMemo(
    () => parseInt(readingType, 10) || 0,
    [readingType]
  );

  // Get random cards for the reading (auto mode)
  const { refetch: refetchCards, isLoading: isLoadingCards } = useQuery({
    queryKey: ["random-cards", readingType],
    queryFn: async () => {
      const response = await axiosClient.get(
        apiUrl(`/api/v1/tarot-cards/random/${readingType}`)
      );
      return response.data as TarotCard[];
    },
    enabled: false, // Don't fetch automatically
  });

  // Load full deck for manual picking (limit to 78)
  interface PaginatedResponse {
    items: TarotCard[];
    total: number;
    page: number;
    limit: number;
    pages: number;
  }

  const { data: deckData, isLoading: isLoadingDeck } = useQuery({
    queryKey: ["full-deck"],
    queryFn: async () => {
      const response = await axiosClient.get(
        apiUrl(`/api/v1/tarot-cards/?page=1&limit=78`)
      );
      return response.data as PaginatedResponse;
    },
    enabled: drawMode === "manual",
    staleTime: 1000 * 60 * 5,
  });

  // Shuffle helper
  function shuffleArray<T>(array: T[]): T[] {
    const a = array.slice();
    for (let i = a.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  // Build a shuffled deck when manual mode active and deck loaded
  useEffect(() => {
    if (drawMode === "manual" && !isLoadingDeck && deckData?.items?.length) {
      setShuffledDeck(shuffleArray(deckData.items));
    }
  }, [drawMode, isLoadingDeck, deckData?.items]);

  // Generate AI reading
  const generateReadingMutation = useMutation({
    mutationFn: async (data: { question: string; cards: TarotCard[] }) => {
      // Try streaming endpoint first for better UX
      setStreamingText("");
      setIsStreaming(true);
      const streamUrl = apiUrl(`/api/v1/ai/generate-reading/stream`);
      const controller = new AbortController();
      abortRef.current = controller;
      const res = await fetch(streamUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: data.question,
          cards: data.cards.map((c) => ({
            ...c,
            is_reversed: !!c.is_reversed,
            order_index: c.order_index ?? 0,
          })),
          reading_type: readingType,
          reading_detail: "quick",
          llm_config: (() => { try { return JSON.parse(localStorage.getItem("tarot_llm_config") || ""); } catch { return undefined; } })()
        }),
        signal: controller.signal,
      });
      if (!res.ok) {
        const response = await axiosClient.post(
          apiUrl("/api/v1/ai/generate-reading"),
          {
            question: data.question,
            cards: data.cards.map((c) => ({
              ...c,
              is_reversed: !!c.is_reversed,
              order_index: c.order_index ?? 0,
            })),
            reading_type: readingType,
            reading_detail: "quick",
            llm_config: (() => { try { return JSON.parse(localStorage.getItem("tarot_llm_config") || ""); } catch { return undefined; } })()
          },
          { headers: { "Content-Type": "application/json" }, timeout: 120000 }
        );
        setIsStreaming(false);
        return response.data;
      }
      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      let fullText = "";
      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value, { stream: true });
          fullText += chunk;
          setStreamingText(fullText);
          // Auto-scroll to the reading panel as content grows
          if (readingRef.current) {
            readingRef.current.scrollIntoView({
              behavior: "smooth",
              block: "start",
            });
          }
        }
      }
      setIsStreaming(false);
      return { response: fullText } as any;
    },
    onSuccess: (data) => {
      setReadingResult({
        question,
        cards: drawnCards || [],
        ai_response:
          streamingText && streamingText.length > 0
            ? streamingText
            : data.response || "Không thể tạo được giải thích.",
        session_id: `session_${Date.now()}`,
      });
      setIsGenerating(false);
    },
    onError: (error: any) => {
      console.error("Error generating reading:", error);
      
      const isRateLimit = error?.response?.status === 429;
      const errorMsg = isRateLimit 
          ? "Bạn đã dùng hết hạn mức đọc bài cho phép ngày hôm nay!" 
          : "Có lỗi xảy ra khi tạo giải thích. Vui lòng thử lại.";
      
      if (isRateLimit && !user) {
        toast.error("Hết lượt dùng thử!", {
          description: "Hãy đăng nhập để nhận thêm 20 lượt đọc mỗi ngày và trải nghiệm cá nhân hóa.",
          duration: 6000
        });
      } else if (isRateLimit) {
        toast.error("Đã đạt giới hạn hôm nay", {
          description: "Tài khoản của bạn đã đạt giới hạn 20 lượt/ngày. Vui lòng quay lại vào ngày mai!"
        });
      }

      setReadingResult({
        question,
        cards: drawnCards || [],
        ai_response: errorMsg,
        session_id: `session_${Date.now()}`,
      });
      setIsGenerating(false);
      setIsStreaming(false);
    },
  });

  // Save reading
  const saveReadingMutation = useMutation({
    mutationFn: async (readingData: any) => {
      const response = await axiosClient.post(
        apiUrl("/api/v1/readings/"),
        readingData
      );
      return response.data;
    },
    onSuccess: () => {
      alert("Đã lưu reading thành công!");
    },
    onError: (error) => {
      console.error("Error saving reading:", error);
      alert("Có lỗi xảy ra khi lưu reading.");
    },
  });

  const handleDrawCards = async () => {
    if (!question.trim()) {
      alert("Vui lòng nhập câu hỏi trước khi rút lá bài.");
      return;
    }
    if (drawMode === "auto") {
      const result = await refetchCards();
      const cards = (result.data || []).map((c: TarotCard, idx: number) => ({
        ...c,
        is_reversed: c.is_reversed ?? false,
        order_index: idx + 1,
      }));
      setDrawnCards(cards);
      setSelectedCards([]);
      setSelectionLocked(true);
      // Scroll to results
      setTimeout(
        () =>
          resultRef.current?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          }),
        50
      );
    } else {
      if (selectedCards.length !== targetCount) {
        alert(`Hãy chọn đủ ${targetCount} lá bài.`);
        return;
      }
      // Preserve selection order as draw order
      const cards = selectedCards.map((c, idx) => ({
        ...c,
        is_reversed: c.is_reversed ?? false,
        order_index: idx + 1,
      }));
      setDrawnCards(cards);
      setSelectionLocked(true);
      // Scroll to results
      setTimeout(
        () =>
          resultRef.current?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          }),
        50
      );
    }
  };

  const handleGenerateReading = async () => {
    if (!drawnCards || drawnCards.length === 0) {
      alert("Vui lòng rút lá bài trước khi tạo giải thích.");
      return;
    }

    setIsGenerating(true);
    setStreamingText("");
    generateReadingMutation.mutate({
      question,
      cards: drawnCards,
    });
    // Scroll to reading area right away
    setTimeout(() => {
      if (readingRef.current) {
        readingRef.current.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    }, 50);
  };

  const toggleReverseAtIndex = (idx: number) => {
    setDrawnCards((prev) =>
      prev.map((c, i) =>
        i === idx ? { ...c, is_reversed: !c.is_reversed } : c
      )
    );
  };

  const handleStopStreaming = () => {
    if (abortRef.current) {
      abortRef.current.abort();
    }
    setIsStreaming(false);
    setIsGenerating(false);
  };

  const handleSaveReading = () => {
    if (!readingResult) {
      alert("Không có reading để lưu.");
      return;
    }

    const readingData = {
      session_id: readingResult.session_id,
      question: readingResult.question,
      cards_drawn: readingResult.cards.map((card) => ({
        card_id: card.id,
        name: card.name,
        name_vi: card.name_vi,
        suit: card.suit,
        arcana: card.arcana,
        number: card.number,
      })),
      ai_response: readingResult.ai_response,
      reading_type: readingType,
      created_at: new Date().toISOString(),
    };

    saveReadingMutation.mutate(readingData);
  };

  const readingTypes = [
    { value: "1", label: "1 lá bài - Câu hỏi đơn giản" },
    { value: "3", label: "3 lá bài - Quá khứ, Hiện tại, Tương lai" },
    { value: "5", label: "5 lá bài - Celtic Cross (Đơn giản)" },
    { value: "7", label: "7 lá bài - Horseshoe" },
    { value: "10", label: "10 lá bài - Celtic Cross (Đầy đủ)" },
  ];

  const handleIntake = async () => {
    if (!question.trim()) {
      alert("Vui lòng nhập câu hỏi trước khi phân tích.");
      return;
    }
    setIsIntaking(true);
    try {
      const res = await axiosClient.post(apiUrl('/api/v1/ai/intake'), { question });
      if (res.data && res.data.recommended_spread) {
        setReadingType(String(res.data.recommended_spread.card_count));
        setIntakeResult({
          name: res.data.recommended_spread.name,
          reason: res.data.reason
        });
      }
    } catch (e) {
      console.error(e);
      alert("Lỗi khi phân tích câu hỏi. Bạn vẫn có thể chọn trải bài thủ công.");
    } finally {
      setIsIntaking(false);
    }
  };

  return (
    <>
      <LLMSettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
      <SEO
        title="Xem bói Tarot - Black Luna Tarot"
        description="Đặt câu hỏi, chọn bài thủ công hoặc tự động, tuỳ chỉnh thứ tự và xuôi/ngược. AI streaming bằng tiếng Việt."
        keywords={["xem bói", "tarot", "AI", "Black Luna Tarot", "streaming"]}
        url="https://example.com/reading"
      />
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="space-y-8"
      >
        {/* Header */}
        <div className="relative text-center space-y-4">
          <Button 
            variant="ghost" 
            size="icon" 
            className="absolute right-0 top-0 rounded-full hover:bg-muted"
            onClick={() => {
              if (!user) {
                toast.info("Tính năng giới hạn", {
                  description: "Bạn cần Đăng Nhập để tùy chỉnh AI Oracle Engine và Persona."
                });
                return;
              }
              setIsSettingsOpen(true)
            }}
            title="Cấu hình AI (Oracle Engine) - Yêu cầu Đăng Nhập"
          >
            <Settings className={`w-6 h-6 transition-colors ${!user ? 'text-muted-foreground/40' : 'text-muted-foreground hover:text-primary'}`} />
          </Button>
          <h1 className="text-4xl font-cinzel font-bold text-gradient">
            Xem bói Tarot
          </h1>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Đặt câu hỏi và rút lá bài để nhận giải thích từ AI thông minh
          </p>
          {!user && (
            <div className="inline-block mt-2 bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300 px-3 py-1 rounded-full text-xs font-medium">
              Chế độ Khách (Guest mode): Tối đa 3 lượt/ngày
            </div>
          )}
        </div>

        {/* Question Input */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              Đặt câu hỏi
            </CardTitle>
            <CardDescription>
              Hãy đặt câu hỏi rõ ràng và cụ thể để nhận được giải thích chính
              xác nhất
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="question">Câu hỏi của bạn</Label>
              <Textarea
                id="question"
                placeholder="Ví dụ: Tôi nên làm gì để cải thiện sự nghiệp của mình?"
                value={question}
                onChange={(e) => {
                  const val = e.target.value;
                  setQuestion(val);
                  if (selectionLocked) {
                    // Changing question allows re-pick
                    setSelectionLocked(false);
                    setSelectedCards([]);
                    setDrawnCards([]);
                    setReadingResult(null);
                  }
                }}
                rows={3}
              />
              <Button onClick={handleIntake} disabled={isIntaking || !question.trim()} variant="secondary" className="w-full mt-2">
                <Wand2 className="mr-2 h-4 w-4 text-purple-500" />
                {isIntaking ? "Đang phân tích ý định..." : "Phân tích câu hỏi & Gọi ý trải bài (AutoHarness)"}
              </Button>
            </div>

            {intakeResult && (
              <motion.div initial={{opacity:0, height:0}} animate={{opacity:1, height:'auto'}} className="bg-purple-50 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-800 p-4 rounded-lg">
                <p className="text-sm font-medium text-purple-800 dark:text-purple-300 mb-1 flex items-center gap-2">
                  <Sparkles className="w-4 h-4" /> Hệ thống AutoHarness đã kích hoạt
                </p>
                <p className="text-xs text-purple-700 dark:text-purple-400">
                  Phân tích: {intakeResult.reason}<br/>
                  Đề xuất: <strong>{intakeResult.name}</strong> ({readingType} lá)
                </p>
              </motion.div>
            )}

            <div className="space-y-2">
              <Label htmlFor="reading-type" className="text-sm font-medium">
                Thiết lập kiểu trải bài {intakeResult ? "(Đã gợi ý)" : "(Thủ công)"}
              </Label>
              <Select value={readingType} onValueChange={setReadingType}>
                <SelectTrigger className="tarot-select-trigger h-11">
                  <SelectValue placeholder="Chọn kiểu trải bài" />
                </SelectTrigger>
                <SelectContent className="tarot-select-content">
                  {readingTypes.map((type) => (
                    <SelectItem
                      key={type.value}
                      value={type.value}
                      className="tarot-select-item py-3"
                    >
                      <div className="flex flex-col">
                        <span className="font-medium">{type.label}</span>
                        <span className="text-xs text-muted-foreground">
                          {type.value === "1" && "Đơn giản, nhanh chóng"}
                          {type.value === "3" && "Tổng quan thời gian"}
                          {type.value === "5" && "Phân tích sâu"}
                        </span>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Draw mode toggle */}
            <div className="space-y-2">
              <Label className="text-sm font-medium">Chế độ rút bài</Label>
              <ToggleGroup
                value={drawMode}
                onValueChange={(v) => {
                  const mode = (v as any) || "auto";
                  setDrawMode(mode);
                  // Reset selection state when switching modes
                  setSelectionLocked(false);
                  setSelectedCards([]);
                  setDrawnCards([]);
                }}
                options={[
                  { value: "auto", label: "Tự động" },
                  { value: "manual", label: "Tự bốc" },
                ]}
                variant="default"
                size="default"
              />
              {drawMode === "manual" && (
                <p className="text-xs text-muted-foreground">
                  Hãy chọn đủ {targetCount} lá từ bộ bài bên dưới, sau đó bấm
                  "Xác nhận lựa chọn".
                </p>
              )}
            </div>

            <div className="flex gap-4">
              <Button
                onClick={handleDrawCards}
                disabled={
                  !question.trim() ||
                  (drawMode === "auto" && isLoadingCards) ||
                  (drawMode === "manual" &&
                    (isLoadingDeck ||
                      selectedCards.length === 0 ||
                      selectionLocked))
                }
                className="flex-1"
              >
                <Shuffle className="mr-2 h-4 w-4" />
                {drawMode === "auto"
                  ? isLoadingCards
                    ? "Đang rút lá bài..."
                    : "Rút ngẫu nhiên"
                  : selectionLocked
                  ? "Đã xác nhận"
                  : "Xác nhận lựa chọn"}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Manual picking deck */}
        {drawMode === "manual" &&
          !selectionLocked &&
          drawnCards.length === 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Eye className="h-5 w-5" />
                  Bộ bài (chọn {selectedCards.length}/{targetCount})
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {isLoadingDeck ? (
                  <p className="text-muted-foreground">Đang tải bộ bài...</p>
                ) : (
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-3">
                    {(shuffledDeck.length
                      ? shuffledDeck
                      : deckData?.items || []
                    ).map((card) => {
                      const isSelected = selectedCards.some(
                        (c) => c.id === card.id
                      );
                      const reachedLimit =
                        selectedCards.length >= targetCount && !isSelected;
                      const imageUrl = card.image_url
                        ? apiUrl(`/api/v1/tarot-cards/image/${card.id}`)
                        : undefined;
                      return (
                        <button
                          key={card.id}
                          type="button"
                          onClick={() => {
                            if (selectionLocked) return;
                            setSelectedCards((prev) => {
                              const exists = prev.some((c) => c.id === card.id);
                              if (exists) {
                                if (selectionLocked) return prev;
                                return prev.filter((c) => c.id !== card.id);
                              }
                              if (prev.length >= targetCount) return prev;
                              return [...prev, card];
                            });
                          }}
                          disabled={reachedLimit || selectionLocked}
                          className={`group relative rounded-md overflow-hidden border transition-all ${
                            isSelected
                              ? "ring-2 ring-primary border-primary shadow-md"
                              : reachedLimit
                              ? "opacity-50 cursor-not-allowed"
                              : "hover:shadow-lg"
                          }`}
                        >
                          <div className="w-full aspect-[3/4] bg-gradient-to-br from-slate-200 to-slate-100 dark:from-slate-800 dark:to-slate-700 flex items-center justify-center">
                            {/* Face-down style */}
                            {!isSelected ? (
                              <img
                                src={BackImage}
                                alt="Card Back"
                                className="h-full w-auto mx-auto object-contain"
                              />
                            ) : imageUrl ? (
                              // Revealed image when selected
                              <img
                                src={imageUrl}
                                alt={card.name_vi}
                                className="h-full w-auto mx-auto object-contain"
                                onError={(e) => {
                                  const target = e.target as HTMLImageElement;
                                  target.style.display = "none";
                                  (
                                    target.nextElementSibling as HTMLDivElement | null
                                  )?.classList.remove("hidden");
                                }}
                              />
                            ) : (
                              <ImageIcon className="w-8 h-8 text-muted-foreground/50" />
                            )}
                          </div>
                          <div className="absolute inset-0 pointer-events-none border border-border/60 rounded-md" />
                        </button>
                      );
                    })}
                  </div>
                )}
                <div className="flex items-center justify-between">
                  <div className="text-sm text-muted-foreground">
                    Đã chọn {selectedCards.length}/{targetCount}
                    {selectionLocked && (
                      <span className="ml-2 text-xs">
                        • Bạn đã xác nhận. Muốn chọn lại, hãy nhập câu hỏi khác.
                      </span>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

        {/* Cards Display */}
        {drawnCards && drawnCards.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Lá bài đã rút ({drawnCards.length} lá)
              </CardTitle>
            </CardHeader>
            <CardContent ref={resultRef}>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
                {drawnCards.map((card, index) => {
                  const imageUrl = card.image_url
                    ? apiUrl(`/api/v1/tarot-cards/image/${card.id}`)
                    : null;

                  return (
                    <motion.div
                      key={card.id}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: index * 0.1, duration: 0.3 }}
                    >
                      <Card className="text-center hover:shadow-lg transition-shadow duration-300">
                        <CardHeader className="pb-2">
                          <div className="relative w-full h-32 bg-gradient-to-br from-mystic-100 to-gold-100 rounded-lg mb-2 overflow-hidden">
                            {/* Order index badge */}
                            <div className="absolute top-1 left-1 text-[11px] px-1.5 py-0.5 rounded bg-black/60 text-white">
                              #{card.order_index || index + 1}
                            </div>
                            {imageUrl ? (
                              <img
                                src={imageUrl}
                                alt={card.name_vi}
                                className={`h-full w-auto mx-auto object-contain transition-transform ${
                                  card.is_reversed ? "rotate-180" : ""
                                }`}
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
                          <CardTitle className="text-sm font-cinzel">
                            {card.name_vi}
                          </CardTitle>
                          <CardDescription className="text-xs">
                            {card.name}
                          </CardDescription>
                        </CardHeader>
                        <CardContent className="pt-0">
                          <div className="flex flex-wrap gap-1 justify-center">
                            <Badge variant="secondary" className="text-xs">
                              {card.suit}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              {card.arcana}
                            </Badge>
                            {card.is_reversed && (
                              <Badge variant="destructive" className="text-xs">
                                Ngược
                              </Badge>
                            )}
                          </div>
                          <div className="mt-2 flex justify-center">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => toggleReverseAtIndex(index)}
                            >
                              {card.is_reversed ? "Để xuôi" : "Đảo ngược"}
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  );
                })}
              </div>

              <div className="mt-6 flex items-center justify-center gap-3">
                <Button
                  onClick={handleGenerateReading}
                  disabled={isGenerating || isStreaming}
                  size="lg"
                  className="px-8"
                >
                  <Sparkles className="mr-2 h-5 w-5" />
                  {isGenerating || isStreaming
                    ? "Đang tạo..."
                    : "Tạo giải thích AI"}
                </Button>
                {isStreaming && (
                  <Button
                    variant="outline"
                    onClick={handleStopStreaming}
                    size="lg"
                  >
                    Dừng
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Reading Result (shows during streaming too) */}
        {(readingResult || streamingText || isStreaming) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card ref={readingRef}>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5" />
                    Giải thích AI
                  </span>
                  <Button
                    onClick={handleSaveReading}
                    variant="outline"
                    size="sm"
                  >
                    <Save className="mr-2 h-4 w-4" />
                    Lưu reading
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h4 className="font-semibold mb-2">Câu hỏi:</h4>
                  <p className="text-muted-foreground italic">
                    "{readingResult ? readingResult.question : question}"
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold mb-2">Giải thích:</h4>
                  <div className="bg-mystic-50/30 dark:bg-mystic-900/10 rounded-xl p-4 sm:p-6 shadow-inner border border-mystic-200/50 dark:border-mystic-800/50">
                    <TarotMarkdownViewer content={streamingText || readingResult?.ai_response || ""} />
                  </div>
                  {(isStreaming || isGenerating) && (
                    <p className="text-xs text-muted-foreground mt-2">
                      Đang tạo nội dung...
                    </p>
                  )}
                </div>

                <div>
                  <h4 className="font-semibold mb-2">Lá bài đã sử dụng:</h4>
                  <div className="flex flex-wrap gap-2">
                    {(readingResult ? readingResult.cards : drawnCards).map(
                      (card) => (
                        <Badge key={card.id} variant="secondary">
                          {card.name_vi}
                        </Badge>
                      )
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Instructions */}
        <Card className="border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-950">
          <CardHeader>
            <CardTitle className="text-blue-800 dark:text-blue-200">
              Hướng dẫn sử dụng
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-blue-700 dark:text-blue-300">
              <p>
                • <strong>Đặt câu hỏi rõ ràng:</strong> Câu hỏi càng cụ thể,
                giải thích càng chính xác
              </p>
              <p>
                • <strong>Chọn kiểu trải bài:</strong> Số lượng lá bài phù hợp
                với độ phức tạp của câu hỏi
              </p>
              <p>
                • <strong>Rút lá bài:</strong> Hệ thống sẽ rút ngẫu nhiên từ bộ
                bài 78 lá
              </p>
              <p>
                • <strong>AI giải thích:</strong> Sử dụng AI để phân tích và đưa
                ra giải thích chi tiết
              </p>
              <p>
                • <strong>Lưu reading:</strong> Lưu lại để tham khảo sau này
              </p>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </>
  );
};

export default Reading;
