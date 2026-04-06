import { motion } from "framer-motion";
import SEO from "@/components/SEO";
import { BookOpen, Heart, Shield, Sparkles, CheckCircle2 } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const About = () => {
  const features = [
    {
      icon: <BookOpen className="h-8 w-8" />,
      title: "API Backend thực tế",
      description: "Sử dụng FastAPI với MongoDB và các API endpoints thực tế",
    },
    {
      icon: <Heart className="h-8 w-8" />,
      title: "LLM-Powered Readings",
      description:
        "Sử dụng mô hình ngôn ngữ lớn để tạo giải thích có chiều sâu",
    },
    {
      icon: <Shield className="h-8 w-8" />,
      title: "Dữ liệu Tarot đầy đủ",
      description: "78 lá bài với thông tin chi tiết và ý nghĩa phong phú",
    },
    {
      icon: <Sparkles className="h-8 w-8" />,
      title: "Frontend hiện đại",
      description: "React + TypeScript + Tailwind CSS + Shadcn UI",
    },
  ];

  return (
    <>
      <SEO
        title="Giới thiệu - Black Luna Tarot"
        description="Dự án Tarot dùng LLM để thay thế các phản hồi cứng nhắc. Xây dựng bằng FastAPI, MongoDB, React, Tailwind."
        keywords={["tarot", "giới thiệu", "Black Luna Tarot", "LLM"]}
        url="https://example.com/about"
        type="article"
      />
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="space-y-12"
      >
        {/* Header */}
        <div className="text-center space-y-6">
          <h1 className="text-4xl font-cinzel font-bold text-gradient">
            Về Black Luna Tarot
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Hệ thống xem bói Tarot được hỗ trợ bởi AI, kết hợp giữa trí tuệ cổ
            đại và công nghệ mô hình ngôn ngữ lớn hiện đại.
          </p>
        </div>

        {/* Mission */}
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl font-cinzel">
              Câu chuyện của Black Luna Tarot
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-lg leading-relaxed text-muted-foreground">
              Chào mọi người, mình là Blackie, một web developer. Hiện tại mình
              đang nghiên cứu và nghịch ngợm về AI và các công nghệ liên quan.
              Người yêu mình là một tarot reader. Bình thường thì mình hay nhờ
              bạn ý bói cho. Mình cũng từng dùng thử một số website bói nhưng
              thấy hơi cứng nhắc và mình không thích lời giải thích của các
              website đó. Vì vậy mình nảy ra ý tưởng nếu như mình có thể tích
              hợp mô hình ngôn ngữ lớn vào hệ thống bói tarot thì sẽ ra sao? Và
              vì vậy mình đã tạo ra Black Luna Tarot. Vụ này mình ko nhờ người
              yêu của mình hỗ trợ mà là tự mình mày mò triển khai nên chắc là
              lúc sơ khai của hệ thống sẽ có nhiều thiếu sót. Minh mong rằng
              mình ko quá lười để dừng phát triển hệ thống này. Mọi người cứ
              dùng thoải mái. Chúc mọi người có những trải nghiệm thú vị và hữu
              ích.
            </p>
          </CardContent>
        </Card>

        {/* Features */}
        <div className="space-y-6">
          <h2 className="text-3xl font-cinzel font-bold text-center text-gradient">
            Tính năng chính
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1, duration: 0.5 }}
              >
                <Card className="h-full text-center hover:shadow-lg transition-shadow duration-300">
                  <CardHeader>
                    <div className="mx-auto mb-4 p-3 rounded-full bg-primary/10 text-primary">
                      {feature.icon}
                    </div>
                    <CardTitle className="font-cinzel">
                      {feature.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription>{feature.description}</CardDescription>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>

        {/* API Architecture */}
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl font-cinzel">
              Kiến trúc API
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              Black Luna Tarot được xây dựng với kiến trúc RESTful API hiện đại,
              tích hợp mô hình ngôn ngữ lớn để thay thế response templates
              truyền thống.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <h4 className="font-semibold text-green-600 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" /> Backend APIs
                </h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Tarot Cards API</li>
                  <li>• Readings API</li>
                  <li>• AI Service API</li>
                  <li>• Sessions API</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h4 className="font-semibold text-blue-600 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" /> Frontend Features
                </h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• Browse Tarot Cards</li>
                  <li>• Search & Filter</li>
                  <li>• LLM Reading Generation</li>
                  <li>• Save Readings</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h4 className="font-semibold text-purple-600 flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4" /> Technologies
                </h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• FastAPI + MongoDB</li>
                  <li>• React + TypeScript</li>
                  <li>• Tailwind CSS</li>
                  <li>• Shadcn UI</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* How It Works */}
        <div className="space-y-6">
          <h2 className="text-3xl font-cinzel font-bold text-center text-gradient">
            Cách hoạt động
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-bold">
                    1
                  </span>
                  Đặt câu hỏi
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Hãy đặt câu hỏi rõ ràng và cụ thể về vấn đề bạn muốn được
                  hướng dẫn.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-bold">
                    2
                  </span>
                  Rút lá bài
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Hệ thống sẽ rút ngẫu nhiên số lượng lá bài phù hợp từ API
                  backend.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-bold">
                    3
                  </span>
                  LLM phân tích
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Mô hình ngôn ngữ lớn sẽ phân tích câu hỏi, bối cảnh và các lá
                  bài để tạo ra lời giải thích cá nhân hoá và sâu sắc.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* API Endpoints */}
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl font-cinzel">
              API Endpoints
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              Hệ thống cung cấp các API endpoints sau:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold mb-2">Tarot Cards API</h4>
                <div className="space-y-1 text-sm text-muted-foreground">
                  <p>• GET /api/v1/tarot-cards/ - Lấy danh sách lá bài</p>
                  <p>
                    • GET /api/v1/tarot-cards/{"{id}"} - Lấy chi tiết lá bài
                  </p>
                  <p>
                    • GET /api/v1/tarot-cards/random/{"{count}"} - Lấy lá bài
                    ngẫu nhiên
                  </p>
                  <p>
                    • GET /api/v1/tarot-cards/search/{"{query}"} - Tìm kiếm lá
                    bài
                  </p>
                </div>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Readings & AI API</h4>
                <div className="space-y-1 text-sm text-muted-foreground">
                  <p>• POST /api/v1/readings/ - Tạo reading mới</p>
                  <p>• GET /api/v1/readings/{"{id}"} - Lấy reading theo ID</p>
                  <p>• POST /api/v1/ai/generate-reading - Tạo AI reading</p>
                  <p>• POST /api/v1/sessions/ - Tạo session mới</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Disclaimer */}
        <Card className="border-orange-200 bg-orange-50 dark:border-orange-800 dark:bg-orange-950">
          <CardHeader>
            <CardTitle className="text-orange-800 dark:text-orange-200">
              Lưu ý quan trọng
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-orange-700 dark:text-orange-300">
              Black Luna Tarot là một dự án nghiên cứu công nghệ, kết quả được
              tạo ra bởi AI chỉ mang tính chất tham khảo và giải trí. Tarot là
              công cụ tự vấn và tìm hiểu bản thân, không phải để dự đoán tương
              lai. Hãy luôn tin tưởng vào trực giác và lý trí của chính mình khi
              đưa ra các quyết định quan trọng.
            </p>
          </CardContent>
        </Card>

        {/* Technical Info */}
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl font-cinzel">
              Thông tin kỹ thuật
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold mb-2">Backend Stack</h4>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary">FastAPI</Badge>
                  <Badge variant="secondary">MongoDB</Badge>
                  <Badge variant="secondary">Motor</Badge>
                  <Badge variant="secondary">Pydantic</Badge>
                  <Badge variant="secondary">Python 3.11+</Badge>
                </div>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Frontend Stack</h4>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary">React 18</Badge>
                  <Badge variant="secondary">TypeScript</Badge>
                  <Badge variant="secondary">Vite</Badge>
                  <Badge variant="secondary">Tailwind CSS</Badge>
                  <Badge variant="secondary">Shadcn UI</Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </>
  );
};

export default About;
