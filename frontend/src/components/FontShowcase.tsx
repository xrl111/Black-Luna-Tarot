import React from "react";
import { TarotSelect, TarotSelectItem } from "@/components/ui/select-variants";
import {
  EnhancedSelect,
  TarotCardSelect,
  MysticalSelect,
} from "@/components/ui/enhanced-select";

const FontShowcase: React.FC = () => {
  return (
    <div className="p-8 space-y-8 bg-gradient-to-br from-slate-50 to-purple-50 dark:from-slate-900 dark:to-purple-900 min-h-screen">
      <div className="max-w-4xl mx-auto space-y-12">
        {/* Main Title */}
        <div className="text-center space-y-4">
          <h1 className="tarot-title mystical-glow">🔮 Hệ thống Tarot AI</h1>
          <p className="tarot-subtitle text-mystic-600 dark:text-mystic-400">
            Khám phá tương lai qua trí tuệ nhân tạo
          </p>
        </div>

        {/* Font Showcase Grid */}
        <div className="grid md:grid-cols-2 gap-8">
          {/* Headings & Display Fonts */}
          <div className="glass-effect p-6 rounded-xl space-y-4">
            <h2 className="text-2xl font-bold text-gold-600 mb-4">
              📚 Font Headings
            </h2>

            <div className="space-y-3">
              <div>
                <p className="text-sm text-muted-foreground">
                  Playfair Display - Elegant & Mystical
                </p>
                <h3 className="font-playfair text-2xl font-bold">
                  Thế Giới Tarot Huyền Bí
                </h3>
                <p className="font-playfair text-base italic text-mystic-600">
                  "Sự thật được bày ra qua từng lá bài"
                </p>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">
                  Cormorant - Gothic & Sophisticated
                </p>
                <h3 className="font-cormorant text-2xl font-semibold">
                  Bí Ẩn Trong Từng Lá Bài
                </h3>
                <p className="font-cormorant text-base italic text-purple-600">
                  "Những câu chuyện cổ xưa được kể lại"
                </p>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">
                  Cinzel Decorative - Ornamental
                </p>
                <h3 className="font-decorative text-xl golden-text">
                  ✨ MA THUẬT CỔ ĐẠI ✨
                </h3>
              </div>
            </div>
          </div>

          {/* Body Text Fonts */}
          <div className="glass-effect p-6 rounded-xl space-y-4">
            <h2 className="text-2xl font-bold text-mystic-600 mb-4">
              📝 Font Body Text
            </h2>

            <div className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">
                  Nunito Sans - Friendly & Vietnamese-optimized
                </p>
                <p className="font-nunito vietnamese-optimized">
                  Hệ thống Tarot AI sử dụng trí tuệ nhân tạo để mang đến những
                  lời giải thích sâu sắc và chính xác về từng lá bài. Với bộ 78
                  lá bài truyền thống, chúng tôi giúp bạn khám phá những bí ẩn
                  của cuộc sống và tương lai.
                </p>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">
                  Source Sans Pro - Clean & Modern
                </p>
                <p className="font-source vietnamese-optimized">
                  Từ những câu hỏi về tình yêu, sự nghiệp, đến những quyết định
                  quan trọng trong cuộc sống, Tarot AI sẽ đồng hành cùng bạn
                  trên hành trình tìm kiếm câu trả lời và hướng dẫn tâm linh.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Card Examples */}
        <div className="space-y-6">
          <h2 className="tarot-subtitle text-center">🃏 Ví dụ về Thẻ Tarot</h2>

          <div className="grid md:grid-cols-3 gap-6">
            {/* Major Arcana Card */}
            <div className="card p-6 hover:shadow-xl transition-all duration-300 hover:scale-105">
              <div className="text-center space-y-3">
                <h3 className="tarot-card-title text-gold-600">
                  The Fool - Kẻ Ngốc
                </h3>
                <div className="text-6xl">🃏</div>
                <p className="tarot-card-text vietnamese-optimized">
                  Khởi đầu mới, cuộc phiêu lưu, sự ngây thơ và tiềm năng vô hạn.
                  Đây là lúc để tin tương vào bản thân và bước vào hành trình
                  mới.
                </p>
                <p className="tarot-mystical text-mystic-600">
                  "Mỗi kết thúc đều là một khởi đầu mới"
                </p>
              </div>
            </div>

            {/* Minor Arcana Card */}
            <div className="card p-6 hover:shadow-xl transition-all duration-300 hover:scale-105">
              <div className="text-center space-y-3">
                <h3 className="tarot-card-title text-mystic-600">
                  Ace of Cups - Át Cốc
                </h3>
                <div className="text-6xl">🏆</div>
                <p className="tarot-card-text vietnamese-optimized">
                  Tình yêu mới, cảm xúc tích cực, sự khởi đầu trong các mối quan
                  hệ. Trái tim bạn đang mở ra để đón nhận những điều tốt đẹp.
                </p>
                <p className="tarot-mystical text-purple-600">
                  "Hãy để trái tim dẫn dắt con đường"
                </p>
              </div>
            </div>

            {/* Court Card */}
            <div className="card p-6 hover:shadow-xl transition-all duration-300 hover:scale-105">
              <div className="text-center space-y-3">
                <h3 className="tarot-card-title text-gold-600">
                  Queen of Wands - Nữ hoàng Gậy
                </h3>
                <div className="text-6xl">👑</div>
                <p className="tarot-card-text vietnamese-optimized">
                  Sự tự tin, lãnh đạo, và năng lượng sáng tạo mạnh mẽ. Bạn có
                  khả năng truyền cảm hứng và dẫn dắt người khác.
                </p>
                <p className="tarot-mystical text-orange-600">
                  "Sức mạnh thật sự đến từ bên trong"
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* AI Reading Example */}
        <div className="glass-effect p-8 rounded-xl">
          <h2 className="tarot-subtitle text-center mb-6 text-mystic-600">
            🤖 Ví dụ Giải Thích AI
          </h2>

          <div className="tarot-reading-text vietnamese-optimized space-y-4 max-w-3xl mx-auto">
            <p className="font-semibold text-gold-600">
              Câu hỏi: "Tình yêu của tôi sẽ như thế nào trong thời gian tới?"
            </p>

            <div className="space-y-3 pl-4 border-l-4 border-mystic-400">
              <p>
                <strong>Quá khứ:</strong> Lá bài{" "}
                <em className="font-cormorant">Three of Swords</em> cho thấy bạn
                đã trải qua những đau khổ trong tình yêu. Những vết thương cảm
                xúc từ các mối quan hệ trước đây vẫn còn ảnh hưởng đến tâm trạng
                hiện tại của bạn.
              </p>

              <p>
                <strong>Hiện tại:</strong>{" "}
                <em className="font-cormorant">The Star</em> mang đến hy vọng và
                sự chữa lành. Đây là thời điểm bạn đang học cách yêu thương bản
                thân và mở lòng với những khả năng mới.
              </p>

              <p>
                <strong>Tương lai:</strong>{" "}
                <em className="font-cormorant">Ten of Cups</em> báo hiệu hạnh
                phúc viên mãn trong tình yêu. Một mối quan hệ ổn định và đầy ý
                nghĩa đang chờ đợi bạn ở phía trước.
              </p>
            </div>

            <p className="italic text-center tarot-mystical mystical-glow">
              "Hành trình tình yêu của bạn đang dẫn đến một kết thúc có hậu đẹp
              đẽ"
            </p>
          </div>
        </div>

        {/* Select Component Showcase */}
        <div className="space-y-6">
          <h2 className="tarot-subtitle text-center">
            🎛️ Enhanced Select Components
          </h2>

          <div className="grid md:grid-cols-3 gap-6">
            {/* Default Select */}
            <div className="glass-effect p-6 rounded-xl space-y-4">
              <h3 className="font-playfair text-lg font-semibold text-center">
                Default Style
              </h3>
              <TarotSelect placeholder="Chọn kiểu trải bài" variant="default">
                <TarotSelectItem value="1">
                  1 lá bài - Câu hỏi đơn giản
                </TarotSelectItem>
                <TarotSelectItem value="3">
                  3 lá bài - Quá khứ, Hiện tại, Tương lai
                </TarotSelectItem>
                <TarotSelectItem value="5">
                  5 lá bài - Celtic Cross (Đơn giản)
                </TarotSelectItem>
              </TarotSelect>
            </div>

            {/* Glass Effect Select */}
            <div className="glass-effect p-6 rounded-xl space-y-4">
              <h3 className="font-playfair text-lg font-semibold text-center">
                Glass Effect
              </h3>
              <TarotSelect placeholder="Chọn bộ bài" variant="glass">
                <TarotSelectItem value="all">Tất cả bộ</TarotSelectItem>
                <TarotSelectItem value="wands">Gậy (Wands)</TarotSelectItem>
                <TarotSelectItem value="cups">Cốc (Cups)</TarotSelectItem>
                <TarotSelectItem value="swords">Kiếm (Swords)</TarotSelectItem>
                <TarotSelectItem value="pentacles">
                  Đồng tiền (Pentacles)
                </TarotSelectItem>
              </TarotSelect>
            </div>

            {/* Mystical Select */}
            <div className="glass-effect p-6 rounded-xl space-y-4">
              <h3 className="font-playfair text-lg font-semibold text-center">
                Mystical Style
              </h3>
              <MysticalSelect
                placeholder="Chọn nguyên tố"
                options={[
                  { value: "all", label: "Tất cả nguyên tố" },
                  { value: "fire", label: "🔥 Lửa (Fire)" },
                  { value: "water", label: "🌊 Nước (Water)" },
                  { value: "air", label: "💨 Khí (Air)" },
                  { value: "earth", label: "🌍 Đất (Earth)" },
                ]}
              />
            </div>
          </div>

          {/* Enhanced Select Showcase */}
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-8">
            {/* Enhanced Select */}
            <div className="glass-effect p-6 rounded-xl space-y-4">
              <h3 className="font-playfair text-lg font-semibold text-center">
                Enhanced Select
              </h3>
              <EnhancedSelect
                placeholder="Chọn difficulty"
                variant="enhanced"
                options={[
                  { value: "beginner", label: "🌱 Người mới bắt đầu" },
                  { value: "intermediate", label: "⭐ Trung cấp" },
                  { value: "advanced", label: "🔥 Nâng cao" },
                  { value: "expert", label: "👑 Chuyên gia" },
                ]}
              />
            </div>

            {/* Tarot Card Select */}
            <div className="glass-effect p-6 rounded-xl space-y-4">
              <h3 className="font-playfair text-lg font-semibold text-center">
                Tarot Card Select
              </h3>
              <TarotCardSelect
                placeholder="Chọn arcana"
                options={[
                  { value: "major", label: "🌟 Major Arcana" },
                  { value: "minor", label: "🎴 Minor Arcana" },
                  { value: "court", label: "👤 Court Cards" },
                ]}
              />
            </div>

            {/* All Variants Demo */}
            <div className="glass-effect p-6 rounded-xl space-y-4 sm:col-span-2 lg:col-span-1">
              <h3 className="font-playfair text-lg font-semibold text-center">
                Focus Test
              </h3>
              <div className="space-y-3">
                <EnhancedSelect
                  placeholder="Focus me with Tab"
                  variant="default"
                  size="sm"
                  options={[
                    { value: "tab1", label: "Tab navigation test" },
                    { value: "tab2", label: "Keyboard accessible" },
                    { value: "tab3", label: "Screen reader friendly" },
                  ]}
                />
                <button className="w-full px-3 py-2 text-sm bg-accent/20 hover:bg-accent/40 rounded-md transition-colors focus:ring-2 focus:ring-ring/40">
                  Next focusable element
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Typography Reference */}
        <div className="text-center text-sm text-muted-foreground space-y-2">
          <p>
            🎨 <strong>Font Stack:</strong> Vietnamese-optimized với fallback hỗ
            trợ
          </p>
          <p className="font-mono text-xs">
            Playfair Display • Cormorant • Nunito Sans • Source Sans Pro •
            Cinzel Decorative
          </p>
        </div>
      </div>
    </div>
  );
};

export default FontShowcase;
