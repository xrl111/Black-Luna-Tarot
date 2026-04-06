import { useState, useEffect } from "react";
import { Settings, X, Key, Cpu, Zap } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { motion, AnimatePresence } from "framer-motion";

export interface LLMSettings {
  provider: string;
  model: string;
  api_key: string;
}

export function LLMSettingsModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [settings, setSettings] = useState<LLMSettings>({
    provider: "ollama",
    model: "qwen2.5:1.5b",
    api_key: "",
  });

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  useEffect(() => {
    const saved = localStorage.getItem("tarot_llm_config");
    if (saved) {
      try {
        setSettings(JSON.parse(saved));
      } catch (e) {}
    }
  }, [isOpen]);

  const handleSave = () => {
    if (settings.provider !== "ollama" && !settings.api_key) {
      alert("Vui lòng nhập API Key cho dịch vụ đã chọn để hệ thống có thể kết nối.");
      return;
    }
    localStorage.setItem("tarot_llm_config", JSON.stringify(settings));
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/85 backdrop-blur-sm">
          <motion.div 
            initial={{ opacity: 0, scale: 0.95, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 10 }}
            className="bg-white dark:bg-slate-800 border dark:border-slate-700 shadow-[0_0_40px_rgba(0,0,0,0.5)] dark:shadow-[0_0_40px_rgba(0,0,0,0.8)] ring-1 ring-white/10 rounded-xl w-full max-w-md overflow-visible relative flex flex-col max-h-[90vh]"
          >
            <div className="flex items-center justify-between p-4 border-b shrink-0">
              <h2 className="text-xl font-cinzel font-semibold flex items-center gap-2">
                <Settings className="w-5 h-5 text-primary" />
                Cấu hình AI (Oracle Engine)
              </h2>
              <Button variant="ghost" size="icon" onClick={onClose} className="rounded-full">
                <X className="w-4 h-4" />
              </Button>
            </div>
            
            <div className="p-6 space-y-5 overflow-y-auto">
              <div className="space-y-2 text-sm text-muted-foreground">
                Đăng nhập bằng mã API của riêng bạn để sử dụng các mô hình AI đỉnh cao thế giới.
              </div>
              <div className="space-y-2">
                <Label className="flex items-center gap-2"><Cpu className="w-4 h-4"/> Nền tảng (Provider)</Label>
                <Select value={settings.provider} onValueChange={(v) => setSettings({...settings, provider: v})}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Chọn nhà cung cấp" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ollama">Ollama (Server cung cấp / Miễn phí)</SelectItem>
                    <SelectItem value="openai">OpenAI (ChatGPT)</SelectItem>
                    <SelectItem value="groq">Groq (Llama, Mixtral)</SelectItem>
                    <SelectItem value="gemini">Google Gemini</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">Ollama là mặc định của hệ thống. Những cổng khác dùng API Key của riêng bạn.</p>
              </div>

              {settings.provider !== "ollama" && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="llm-model" className="flex items-center gap-2"><Zap className="w-4 h-4"/> Tên mô hình (Model Name)</Label>
                    <Input 
                      id="llm-model"
                      name="llm-model"
                      placeholder="VD: gpt-4o, llama-3.3-70b-versatile, gemini-1.5-pro" 
                      value={settings.model || ""} 
                      onChange={(e) => setSettings({...settings, model: e.target.value})} 
                      autoComplete="off"
                      spellCheck={false}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="llm-api-key" className="flex items-center gap-2"><Key className="w-4 h-4"/> API Key</Label>
                    <Input 
                      id="llm-api-key"
                      name="llm-api-key"
                      type="password" 
                      placeholder="sk-..." 
                      value={settings.api_key || ""} 
                      onChange={(e) => setSettings({...settings, api_key: e.target.value})} 
                      autoComplete="off"
                      data-1p-ignore="true"
                      data-lpignore="true"
                    />
                    <p className="text-[11px] text-muted-foreground text-orange-500">
                      Mã này được lưu cục bộ trên máy của bạn (Browser Storage), hệ thống cam kết không bao giờ lưu trữ trên Server.
                    </p>
                  </div>
                </>
              )}
            </div>

            <div className="p-4 border-t bg-muted/30 flex justify-end gap-3 shrink-0 rounded-b-xl">
              <Button variant="outline" onClick={onClose}>Hủy gán</Button>
              <Button onClick={handleSave}>Lưu Cài Đặt Khóa</Button>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
