import { useState, useEffect } from "react";
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
  }, [user]);

  if (isLoading) return <div className="text-center py-20">Đang tải...</div>;

  if (!user) {
    toast.error("Bạn cần đăng nhập để truy cập cài đặt");
    return <Navigate to="/" />;
  }

  const handleSave = async () => {
    setSaving(true);
    try {
      await updatePreferences(formData);
      toast.success("Cập nhật cài đặt thành công!");
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
        <CardHeader>
          <CardTitle className="text-2xl font-cinzel text-mystic-600 dark:text-mystic-400">
            Cá Nhân Hóa Trải Nghiệm (Persona)
          </CardTitle>
          <CardDescription>
            Thiết lập phong cách đọc bài AI Tarot để phù hợp nhất với bản thân bạn.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
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
