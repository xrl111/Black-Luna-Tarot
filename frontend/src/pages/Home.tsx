import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Sparkles, Square, Eye, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import SEO from "@/components/SEO";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const Home = () => {
  const features = [
    {
      icon: <Square className="h-8 w-8" />,
      title: "Bộ bài đầy đủ",
      description:
        "Khám phá 78 lá bài Tarot với ý nghĩa chi tiết và thông tin phong phú",
    },
    {
      icon: <Eye className="h-8 w-8" />,
      title: "Xem bói AI",
      description: "Trải nghiệm xem bói Tarot với AI thông minh",
    },
    {
      icon: <BookOpen className="h-8 w-8" />,
      title: "Tìm kiếm & Lọc",
      description: "Tìm kiếm lá bài theo tên, bộ, hoặc từ khóa",
    },
    {
      icon: <Sparkles className="h-8 w-8" />,
      title: "Lá bài ngẫu nhiên",
      description: "Rút lá bài ngẫu nhiên cho việc xem bói",
    },
  ];

  return (
    <>
      <SEO
        title="Black Luna Tarot - Xem bói Tarot bằng AI (Tiếng Việt)"
        description="Trải nghiệm xem bói Tarot với AI dùng LLM. Streaming, chọn bài thủ công, và giải thích sâu sắc bằng tiếng Việt."
        keywords={[
          "tarot",
          "AI tarot",
          "Black Luna Tarot",
          "xem bài tarot",
          "tiếng Việt",
        ]}
        url="https://example.com/"
      />
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="space-y-16"
      >
        {/* Hero Section */}
        <section className="text-center space-y-8 py-16">
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="space-y-4"
          >
            <h1 className="text-4xl md:text-6xl font-cinzel font-bold text-gradient">
              Khám phá bí ẩn Tarot
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Trải nghiệm xem bói Tarot với AI thông minh. Tìm hiểu ý nghĩa sâu
              sắc của từng lá bài và khám phá vận mệnh của bạn.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4, duration: 0.5 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <Button asChild size="lg" className="text-lg px-8 py-6">
              <Link to="/reading">
                <Sparkles className="mr-2 h-5 w-5" />
                Bắt đầu xem bói
              </Link>
            </Button>
            <Button
              asChild
              variant="outline"
              size="lg"
              className="text-lg px-8 py-6"
            >
              <Link to="/cards">
                <Square className="mr-2 h-5 w-5" />
                Xem bộ bài
              </Link>
            </Button>
          </motion.div>
        </section>

        {/* Features Section */}
        <section className="space-y-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6, duration: 0.5 }}
            className="text-center space-y-4"
          >
            <h2 className="text-3xl font-cinzel font-bold text-gradient">
              Tính năng chính
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Hệ thống Tarot Online được thiết kế dựa trên các API thực tế có
              sẵn
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 + index * 0.1, duration: 0.5 }}
              >
                <Card className="h-full hover:shadow-lg transition-shadow duration-300">
                  <CardHeader className="text-center">
                    <div className="mx-auto mb-4 p-3 rounded-full bg-primary/10 text-primary">
                      {feature.icon}
                    </div>
                    <CardTitle className="font-cinzel">
                      {feature.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-center">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </section>

        {/* API Status Section */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.0, duration: 0.5 }}
          className="text-center space-y-6 py-16"
        >
          <div className="space-y-4">
            <h2 className="text-3xl font-cinzel font-bold text-gradient">
              API Backend Status
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Hệ thống sử dụng các API thực tế từ backend FastAPI
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto">
            <Card className="text-center">
              <CardHeader>
                <CardTitle className="text-green-600">
                  ✅ Tarot Cards API
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  CRUD operations, search, filtering, random cards
                </p>
              </CardContent>
            </Card>
            <Card className="text-center">
              <CardHeader>
                <CardTitle className="text-green-600">
                  ✅ Readings API
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  Create, read, update, delete readings
                </p>
              </CardContent>
            </Card>
            <Card className="text-center">
              <CardHeader>
                <CardTitle className="text-green-600">
                  ✅ AI Service API
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  AI-powered reading generation
                </p>
              </CardContent>
            </Card>
          </div>
        </motion.section>

        {/* CTA Section */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2, duration: 0.5 }}
          className="text-center space-y-6 py-16"
        >
          <div className="space-y-4">
            <h2 className="text-3xl font-cinzel font-bold text-gradient">
              Sẵn sàng khám phá?
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Bắt đầu hành trình khám phá bí ẩn Tarot ngay hôm nay với các API
              thực tế.
            </p>
          </div>
          <Button asChild size="lg" className="text-lg px-8 py-6">
            <Link to="/reading">
              <Sparkles className="mr-2 h-5 w-5" />
              Bắt đầu ngay
            </Link>
          </Button>
        </motion.section>
      </motion.div>
    </>
  );
};

export default Home;
