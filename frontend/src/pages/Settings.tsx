import { useState, useEffect } from "react";
import { Cpu, Zap, Key, User, Bot } from "lucide-react";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Navigate } from "react-router-dom";
import { toast } from "sonner";
import { motion } from "framer-motion";

const Settings = () => {
  const { user, updatePreferences, isLoading } = useAuth();
  const [formData, setFormData] = useState({
    reading_style: "detailed",
    experience_level: "beginner",
    tarot_tradition: "rider_waite",
    belief_system: "spiritual_but_practical"
  });
  
  // LLM Config state
  const [llmSettings, setLlmSettings] = useState({
    provider: "ollama",
    model: "qwen2.5:1.5b",
    api_key: "",
  });

  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user?.preferences) {
      setFormData({
        reading_style: user.preferences.reading_style || "detailed",
        experience_level: user.preferences.experience_level || "beginner",
        tarot_tradition: user.preferences.tarot_tradition || "rider_waite",
        belief_system: user.preferences.belief_system || "spiritual_but_practical"
      });
    }

    // Load LLM Settings from local storage
    const savedLlm = localStorage.getItem("tarot_llm_config");
    if (savedLlm) {
      try {
        setLlmSettings(JSON.parse(savedLlm));
      } catch (e) {}
    }
  }, [user]);

  if (isLoading) return <div className="text-center py-20">Đang tải...</div>;

  if (!user) {
    toast.error("Bạn cần đăng nhập để truy cập cài đặt");
    return <Navigate to="/" />;
  }

  const handleSave = async () => {
    if (llmSettings.provider !== "ollama" && !llmSettings.api_key) {
      toast.error("Vui lòng nhập API Key cho dịch vụ LLM đã chọn để hệ thống có thể kết nối.");
      return;
    }

    setSaving(true);
    try {
      // 1. Save Persona to Backend
      await updatePreferences(formData);
      // 2. Save LLM config to local storage
      localStorage.setItem("tarot_llm_config", JSON.stringify(llmSettings));
      
      toast.success("Cập nhật toàn bộ cấu hình thành công!");
    } catch (error) {
      toast.error("Có lỗi xảy ra khi lưu cài đặt.");
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="max-w-2xl mx-auto"
    >
      <Card className="border-mystic-500/20 bg-background/80 backdrop-blur-sm">
        <CardHeader className="border-b mb-6">
          <CardTitle className="text-2xl font-cinzel text-mystic-600 dark:text-mystic-400">
            Trung Tâm Cài Đặt (Settings Center)
          </CardTitle>
          <CardDescription>
            Quản lý cả tính cách của AI (Persona) lẫn cấu hình động cơ não bộ (LLM Engine).
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-8">
          
          {/* Section 1: Persona */}
          <div className="space-y-6">
            <h3 className="text-lg font-bold flex items-center gap-2 text-primary">
              <User className="w-5 h-5" />
              1. Cá Nhân Hóa (AI Persona)
            </h3>
            <div className="space-y-2">
            <label className="text-sm font-medium">Phong cách đọc bài (Reading Style)</label>
            <select 
              className="w-full p-2 rounded-md border bg-background"
              value={formData.reading_style}
              onChange={(e) => handleChange('reading_style', e.target.value)}
            >
              <option value="detailed">Chi tiết (Detailed)</option>
              <option value="direct">Trực diện & Thực tế (Direct)</option>
              <option value="storytelling">Kể chuyện mộng mơ (Storytelling)</option>
              <option value="academic">Học thuật (Academic)</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Trình độ Tarot của bạn</label>
            <select 
              className="w-full p-2 rounded-md border bg-background"
              value={formData.experience_level}
              onChange={(e) => handleChange('experience_level', e.target.value)}
            >
              <option value="beginner">Người mới (Beginner)</option>
              <option value="intermediate">Biết căn bản (Intermediate)</option>
              <option value="advanced">Chuyên gia Tarot (Advanced)</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Truyền thống bài mong muốn</label>
            <select 
              className="w-full p-2 rounded-md border bg-background"
              value={formData.tarot_tradition}
              onChange={(e) => handleChange('tarot_tradition', e.target.value)}
            >
              <option value="rider_waite">Rider-Waite-Smith (Phổ biến nhất)</option>
              <option value="thoth">Thoth Tarot (Huyền học)</option>
              <option value="marseille">Tarot de Marseille</option>
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Hệ tư tưởng</label>
            <select 
              className="w-full p-2 rounded-md border bg-background"
              value={formData.belief_system}
              onChange={(e) => handleChange('belief_system', e.target.value)}
            >
              <option value="spiritual_but_practical">Tâm linh pha lẫn Thực tế</option>
              <option value="purely_spiritual">Hoàn toàn Tâm linh & Thần bí</option>
              <option value="psychological">Phân tích Tâm lý học</option>
            </select>
          </div>
          </div>

          <hr className="border-mystic-500/20" />

          {/* Section 2: LLM Config */}
          <div className="space-y-6">
            <h3 className="text-lg font-bold flex items-center gap-2 text-primary">
              <Bot className="w-5 h-5" />
              2. Động Cơ Não Bộ AI (Oracle Engine)
            </h3>
            <p className="text-sm text-muted-foreground">Ollama là mặc định (chạy máy chủ nội bộ miễn phí). Bạn có thể cấu hình API ngoài để AI thông minh vượt trội hơn.</p>

            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2"><Cpu className="w-4 h-4"/> Nền tảng (Provider)</label>
              <select 
                className="w-full p-2 rounded-md border bg-background"
                value={llmSettings.provider}
                onChange={(e) => setLlmSettings({...llmSettings, provider: e.target.value})}
              >
                <option value="ollama">Ollama (Mặc định - Cục bộ)</option>
                <option value="openai">OpenAI (ChatGPT)</option>
                <option value="groq">Groq (Llama, Mixtral)</option>
                <option value="gemini">Google Gemini</option>
              </select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium flex items-center gap-2"><Zap className="w-4 h-4"/> Tên mô hình (Model Name)</label>
              <Input 
                placeholder="VD: gpt-4o, llama-3.3-70b, gemma4:latest" 
                value={llmSettings.model} 
                onChange={(e) => setLlmSettings({...llmSettings, model: e.target.value})} 
                autoComplete="off"
                spellCheck={false}
              />
            </div>

            {llmSettings.provider !== "ollama" && (
              <div className="space-y-2">
                <label className="text-sm font-medium flex items-center gap-2"><Key className="w-4 h-4"/> API Key</label>
                <Input 
                  type="password" 
                  placeholder="sk-..." 
                  value={llmSettings.api_key} 
                  onChange={(e) => setLlmSettings({...llmSettings, api_key: e.target.value})} 
                  autoComplete="off"
                />
                <p className="text-[11px] text-muted-foreground text-orange-500">
                  Mã API lưu cục bộ trên máy của bạn (Browser Storage), không lưu trên Server Black Luna Tarot.
                </p>
              </div>
            )}
          </div>

        </CardContent>

        <CardFooter className="flex justify-end gap-3 border-t pt-6 mt-6 border-mystic-500/20">
          <Button variant="outline" onClick={() => window.history.back()}>
            Quay lại
          </Button>
          <Button 
            className="bg-mystic-600 hover:bg-mystic-700 text-white" 
            onClick={handleSave} 
            disabled={saving}
          >
            {saving ? "Đang lưu..." : "Lưu cài đặt Persona"}
          </Button>
        </CardFooter>
      </Card>
    </motion.div>
  );
};

export default Settings;
